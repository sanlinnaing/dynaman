resource "aws_ssm_parameter" "mongodb_url" {
  name        = "/${var.project_name}/${var.environment}/MONGODB_URL"
  description = "MongoDB Connection String"
  type        = "SecureString"
  value       = var.mongodb_url

  tags = {
    Environment = var.environment
  }
}

resource "aws_ssm_parameter" "jwt_secret_key" {
  name        = "/${var.project_name}/${var.environment}/JWT_SECRET_KEY"
  description = "JWT Secret Key for signing tokens"
  type        = "SecureString"
  value       = var.jwt_secret_key

  tags = {
    Environment = var.environment
  }
}
