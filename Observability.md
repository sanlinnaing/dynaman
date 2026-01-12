# Observability Strategy: Custom Metrics vs. OpenTelemetry

This document summarizes the discussion on observability strategies for the Dynaman project, covering the trade-offs between using direct custom metrics and adopting the OpenTelemetry standard.

## Initial Question: Custom Metrics vs. OpenTelemetry

The primary question was to understand the difference between implementing custom metrics manually versus using OpenTelemetry with AWS CloudWatch, especially concerning cost and implementation effort.

### High-Level Comparison

| Feature | Custom Metrics (e.g., using `boto3`) | CloudWatch with OpenTelemetry |
| :--- | :--- | :--- |
| **Concept** | **Direct API Interaction.** Manually construct and send metric data directly to the CloudWatch API. | **Standardized Instrumentation.** Use a vendor-neutral API (OTel) in the app, which then sends data to a backend via a configurable "exporter". |
| **Implementation** | Entirely manual. Requires writing specific code for every single metric. | **Automatic & Manual.** Provides auto-instrumentation for frameworks (FastAPI) to capture standard signals (latency, errors) with minimal setup. |
| **Flexibility** | **Low (Vendor Lock-in).** Code is tightly coupled to the AWS `boto3` SDK. Switching providers requires a complete rewrite of monitoring code. | **High (Vendor-Neutral).** Application code is decoupled from the backend. Switching from CloudWatch to another provider is a configuration change. |
| **Cost** | **Direct Cost:** Standard CloudWatch ingestion fees. **Indirect Cost:** High development and maintenance time. | **Direct Cost:** Ingestion fees are the same. **Indirect Cost:** Lower long-term development cost. A small compute cost exists if using the Collector. |
| **Features**| **Metrics only.** | **Metrics, Traces, and Logs.** OTel is designed to handle all three pillars of observability, allowing for rich, correlated data. |

### Does OpenTelemetry create more metrics?

Yes, out-of-the-box, OTel's auto-instrumentation captures a comprehensive set of standard metrics (e.g., latency histograms for every API endpoint), which is more than you would create manually.

However, this is a feature. It provides a rich, detailed view of system health from the start. Crucially, **you have full control to manage cost** by configuring **Views** in the SDK or **Processors** in the Collector to filter, aggregate, or drop metrics before they are sent to CloudWatch.

## The Role of the OpenTelemetry Collector

The next question was about the components needed on the AWS side and the concept of a "sidecar container".

There are two main patterns to get OTel data to CloudWatch:

### Path 1: Direct Export
The application uses an AWS-specific exporter within the OTel SDK to send data directly to CloudWatch APIs.

**Flow:**
`[Your Python App + OTel SDK + AWS Exporter] ----(HTTPS)----> [AWS CloudWatch API]`

### Path 2: Collector Sidecar (Recommended)
The application sends its data to an OTel Collector running as a **sidecar container** alongside the application container in the same ECS Task. The Collector then forwards the data to CloudWatch.

**Flow:**
`[Your App (OTel SDK)] --(localhost)--> [OTel Collector (Sidecar)] --(HTTPS)--> [AWS CloudWatch API]`

**Associated Costs:**
*   **CloudWatch Ingestion Cost:** No change. This is the same in both patterns.
*   **Compute Cost:** This pattern introduces a small, additional compute cost because the sidecar container requires its own CPU and memory allocation in the ECS task.

The benefits of the collector (improved performance, reliability, centralized configuration) generally outweigh its small compute cost.

## Cluster Capacity Analysis

A request was made to analyze the existing Terraform code to determine if the ECS cluster could handle the additional resource load of an OTel Collector sidecar.

### Analysis Summary

1.  **ECS Node:** The cluster runs on a single `t4g.small` instance, which provides **2048 CPU units** and **2048 MiB of memory**.
2.  **Current Usage:** The 6 running tasks reserve a total of **1536 CPU units (75%)** and **1536 MiB of memory (75%)**.
3.  **Sidecar Impact:** Adding a sidecar with an estimated **128 CPU units** and **128 MiB memory** to the 4 backend tasks results in a new total reservation.
    *   **New Total CPU:** (2 tasks × 256) + (4 tasks × 384) = **2048 CPU units**
    *   **New Total Memory:** (2 tasks × 256) + (4 tasks × 384) = **2048 MiB**

### Conclusion

**Yes, the `t4g.small` node is technically sufficient, but it will be at 100% resource reservation.** This is risky and leaves no buffer for the OS, the ECS agent, or deployment activities.

**Recommendation:** To safely run with the OTel Collector sidecar, the instance type should be upgraded to a **`t4g.medium`** to provide a healthy resource buffer.
