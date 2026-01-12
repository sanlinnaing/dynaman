# Prepare OTel Collector configuration
locals {
  # Common OTel configuration for all services
  otel_config = {
    receivers = {
      otlp = {
        protocols = {
          grpc = { endpoint = "0.0.0.0:4317" }
          http = { endpoint = "0.0.0.0:4318" }
        }
      }
      # We define nginx here, but only include it in the pipeline for the UI
      nginx = {
        endpoint            = "http://localhost:80/nginx_status"
        collection_interval = "10s"
      }
    }
    connectors = {
      spanmetrics = {
        histogram = {
          explicit = {
            buckets = ["2ms", "6ms", "10ms", "100ms", "250ms", "500ms", "1s", "5s"]
          }
        }
        dimensions = [
          { name = "http.request.method" },
          { name = "http.response.status_code" },
          { name = "deployment.environment" }
        ]
      }
    }
    processors = {
      batch             = { send_batch_size = 8192, timeout = "10s" }
      cumulativetodelta = null
      resourcedetection = { detectors = ["env", "system"] }
    }
    exporters = {
      "otlphttp/newrelic" = {
        endpoint = "https://otlp.nr-data.net"
        headers  = { "api-key" = "$${NEW_RELIC_INGEST_KEY}" }
      }
      debug = { verbosity = "detailed" }
    }
  }

  # Pipeline for UI (includes Nginx)
  ui_otel_service = {
    pipelines = {
      traces  = { receivers = ["otlp"], processors = ["resourcedetection", "batch"], exporters = ["otlphttp/newrelic", "spanmetrics"] }
      metrics = { receivers = ["otlp", "spanmetrics", "nginx"], processors = ["resourcedetection", "cumulativetodelta", "batch"], exporters = ["otlphttp/newrelic", "debug"] }
    }
  }

  # Pipeline for Backend (No Nginx)
  backend_otel_service = {
    pipelines = {
      traces  = { receivers = ["otlp"], processors = ["resourcedetection", "batch"], exporters = ["otlphttp/newrelic", "spanmetrics"] }
      metrics = { receivers = ["otlp", "spanmetrics"], processors = ["resourcedetection", "cumulativetodelta", "batch"], exporters = ["otlphttp/newrelic", "debug"] }
    }
  }
}

# UI Service
resource "aws_ecs_task_definition" "ui" {
  family                   = "${var.project_name}-ui"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = 256
  memory                   = 256
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "ui"
      image     = aws_ecr_repository.ui.repository_url
      cpu       = 256
      memory    = 256
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 0 # Dynamic port mapping
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ui"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "ui" {
  name            = "${var.project_name}-ui"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.ui.arn
  desired_count   = 2
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.ui.arn
    container_name   = "ui"
    container_port   = 80
  }
}

# Auth Service
resource "aws_ecs_task_definition" "auth" {
  family                   = "${var.project_name}-auth"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = 256
  memory                   = 256
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "auth"
      image     = aws_ecr_repository.auth.repository_url
      cpu       = 256
      memory    = 256
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 0
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DATABASE_NAME", value = "dynaman_auth" },
        { name = "OTEL_ENABLED", value = "false" },
        { name = "OTEL_SERVICE_NAME", value = "auth-service" },
        
        { name = "OTEL_EXPORTER_OTLP_PROTOCOL", value = "http/protobuf" },
        { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = "http://localhost:4318" },

        { name = "OTEL_EXPORTER_OTLP_INSECURE", value = "true" },
        { name = "APP_ENVIRONMENT", value = "production" }
      ]
      secrets = [
        { name = "MONGODB_URL", valueFrom = data.aws_secretsmanager_secret.mongodb_url.arn },
        { name = "SECRET_KEY", valueFrom = data.aws_secretsmanager_secret.jwt_secret_key.arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "auth"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "auth" {
  name            = "${var.project_name}-auth"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.auth.arn
  desired_count   = 2
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.auth.arn
    container_name   = "auth"
    container_port   = 8000
  }
}

# Engine Metadata Service
resource "aws_ecs_task_definition" "meta" {
  family                   = "${var.project_name}-meta"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = 256
  memory                   = 256
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "meta"
      image     = aws_ecr_repository.engine.repository_url
      cpu       = 256
      memory    = 256
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 0
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DATABASE_NAME", value = "dynaman" },
        { name = "APP_MODE", value = "metadata" },
        { name = "OTEL_ENABLED", value = "false" },
        { name = "OTEL_SERVICE_NAME", value = "engine-meta" },

        { name = "OTEL_EXPORTER_OTLP_PROTOCOL", value = "http/protobuf" },
        { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = "http://localhost:4318" },

        { name = "OTEL_EXPORTER_OTLP_INSECURE", value = "true" },
        { name = "APP_ENVIRONMENT", value = "production" }
      ]
      secrets = [
        { name = "MONGODB_URL", valueFrom = data.aws_secretsmanager_secret.mongodb_url.arn },
        { name = "SECRET_KEY", valueFrom = data.aws_secretsmanager_secret.jwt_secret_key.arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "meta"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "meta" {
  name            = "${var.project_name}-meta"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.meta.arn
  desired_count   = 1
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.engine_meta.arn
    container_name   = "meta"
    container_port   = 8000
  }
}

# Engine Execution Service
resource "aws_ecs_task_definition" "exec" {
  family                   = "${var.project_name}-exec"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = 256
  memory                   = 256
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "exec"
      image     = aws_ecr_repository.engine.repository_url
      cpu       = 256
      memory    = 256
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 0
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DATABASE_NAME", value = "dynaman" },
        { name = "APP_MODE", value = "execution" },
        { name = "OTEL_ENABLED", value = "false" },
        { name = "OTEL_SERVICE_NAME", value = "engine-exec" },

        { name = "OTEL_EXPORTER_OTLP_PROTOCOL", value = "http/protobuf" },
        { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = "http://localhost:4318" },

        { name = "OTEL_EXPORTER_OTLP_INSECURE", value = "true" },
        { name = "APP_ENVIRONMENT", value = "production" }
      ]
      secrets = [
        { name = "MONGODB_URL", valueFrom = data.aws_secretsmanager_secret.mongodb_url.arn },
        { name = "SECRET_KEY", valueFrom = data.aws_secretsmanager_secret.jwt_secret_key.arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "exec"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "exec" {
  name            = "${var.project_name}-exec"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.exec.arn
  desired_count   = 2
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.engine_exec.arn
    container_name   = "exec"
    container_port   = 8000
  }
}
