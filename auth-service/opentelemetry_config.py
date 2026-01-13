import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_opentelemetry(app):
    """Configure OpenTelemetry for the application."""

    if os.environ.get("OTEL_ENABLED") != "true":
        print("OpenTelemetry is disabled.")
        return

    print("OpenTelemetry is enabled. Initializing...")
    # Get the service name from an environment variable, default to 'auth-service'
    service_name = os.environ.get("OTEL_SERVICE_NAME", "auth-service")
    deployment_environment = os.environ.get("APP_ENVIRONMENT", "unknown")

    # Set up a resource with the service name
    resource = Resource(attributes={
        "service.name": service_name,
        "deployment.environment": deployment_environment,
    })

    # --- TRACES SETUP ---
    # Set up a TracerProvider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure the OTLP exporter to send data to the collector sidecar
    # The endpoint is the default for the OTel Collector's gRPC port
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True  # Use insecure connection for localhost communication
    )

    # Use a BatchSpanProcessor to send spans in batches
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    # ---------------------

    # --- METRICS SETUP ---
    # Configure the Metric Exporter (pointing to Collector gRPC port)
    metric_exporter = OTLPMetricExporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True
    )

    # Metrics are sent periodically (default is every 60s)
    reader = PeriodicExportingMetricReader(metric_exporter)

    # Set up the MeterProvider with the same resource tags
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
    # ---------------------

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

    # Instrument Pymongo for MongoDB queries (which covers motor)
    def request_hook(span, event):
        if not span or not span.is_recording():
            return

        # REQUIRED for New Relic DB UI
        span.set_attribute("db.system", "mongodb")
        span.set_attribute("db.operation", event.command_name)

        # Database name
        if event.database_name:
            span.set_attribute("db.name", event.database_name)
            span.set_attribute("db.namespace", event.database_name)

        # Collection name (best-effort)
        if hasattr(event, "command") and event.command:
            collection = event.command.get(event.command_name)
            if isinstance(collection, str):
                span.set_attribute("db.collection.name", collection)

    # Apply the instrumentation with the hook
    PymongoInstrumentor().instrument(tracer_provider=tracer_provider, request_hook=request_hook)

    # Instrument the requests library for any outgoing HTTP calls
    RequestsInstrumentor().instrument(tracer_provider=tracer_provider)
