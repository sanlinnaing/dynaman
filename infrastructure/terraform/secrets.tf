data "aws_secretsmanager_secret" "mongodb_url" {
  name = "/${var.project_name}/${var.environment}/MONGODB_URL"
}

data "aws_secretsmanager_secret_version" "mongodb_url" {
  secret_id = data.aws_secretsmanager_secret.mongodb_url.id
}

data "aws_secretsmanager_secret" "jwt_secret_key" {
  name = "/${var.project_name}/${var.environment}/JWT_SECRET_KEY"
}

data "aws_secretsmanager_secret_version" "jwt_secret_key" {
  secret_id = data.aws_secretsmanager_secret.jwt_secret_key.id
}

data "aws_secretsmanager_secret" "NEW_RELIC_INGEST_KEY" {
  name = "/${var.project_name}/${var.environment}/NEW_RELIC_INGEST_KEY"
}

data "aws_secretsmanager_secret_version" "NEW_RELIC_INGEST_KEY" {
  secret_id = data.aws_secretsmanager_secret.NEW_RELIC_INGEST_KEY.id
}


