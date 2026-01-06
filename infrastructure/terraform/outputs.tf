output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_urls" {
  description = "URLs of the ECR repositories"
  value = {
    ui     = aws_ecr_repository.ui.repository_url
    auth   = aws_ecr_repository.auth.repository_url
    engine = aws_ecr_repository.engine.repository_url
  }
}
