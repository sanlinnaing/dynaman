resource "aws_ecr_repository" "ui" {
  name                 = "${var.project_name}-ui"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "auth" {
  name                 = "${var.project_name}-auth"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "engine" {
  name                 = "${var.project_name}-engine"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

# Lifecycle Policy to clean up old images
locals {
  lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "ui_policy" {
  repository = aws_ecr_repository.ui.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "auth_policy" {
  repository = aws_ecr_repository.auth.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "engine_policy" {
  repository = aws_ecr_repository.engine.name
  policy     = local.lifecycle_policy
}
