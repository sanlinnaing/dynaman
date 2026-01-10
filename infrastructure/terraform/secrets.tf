resource "aws_secretsmanager_secret" "mongodb_url" {
  name        = "/${var.project_name}/${var.environment}/MONGODB_URL"
  description = "MongoDB Connection String"
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "mongodb_url" {
  secret_id     = aws_secretsmanager_secret.mongodb_url.id
  secret_string = var.mongodb_url
}

resource "aws_secretsmanager_secret" "jwt_secret_key" {
  name        = "/${var.project_name}/${var.environment}/JWT_SECRET_KEY"
  description = "JWT Secret Key for signing tokens"
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret_key" {
  secret_id     = aws_secretsmanager_secret.jwt_secret_key.id
  secret_string = var.jwt_secret_key
}
