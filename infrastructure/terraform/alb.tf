resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-alb"
  }
}

# Target Groups
resource "aws_lb_target_group" "ui" {
  name_prefix = "ui-"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance" # ECS awsvpc network mode

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 60
    interval            = 300
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_target_group" "auth" {
  name_prefix = "auth-"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 60
    interval            = 300
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_target_group" "engine_meta" {
  name_prefix = "meta-"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    path                = "/api/v1/schemas/openapi.json"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 60
    interval            = 300
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_target_group" "engine_exec" {
  name_prefix = "exec-"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    path                = "/api/v1/data/openapi.json"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 60
    interval            = 300
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }
}

# Listener Rules
resource "aws_lb_listener_rule" "auth" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.auth.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/auth/*"]
    }
  }
}

resource "aws_lb_listener_rule" "engine_meta" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 110

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.engine_meta.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/schemas/*"]
    }
  }
}

resource "aws_lb_listener_rule" "engine_exec" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 120

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.engine_exec.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/data/*"]
    }
  }
}
