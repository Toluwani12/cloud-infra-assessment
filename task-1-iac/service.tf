resource "aws_ecs_service" "app" {
  name            = "assessment-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn

  launch_type   = "FARGATE"
  desired_count = 2

  availability_zone_rebalancing = "ENABLED"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 60

  enable_ecs_managed_tags = true
  propagate_tags          = "SERVICE"

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8080
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

  depends_on = [
    aws_lb_listener.http,
    aws_route_table_association.public,
    aws_route_table_association.private,
    aws_iam_role_policy_attachment.ecs_execution,
    aws_vpc_security_group_ingress_rule.public_http,
    aws_vpc_security_group_egress_rule.alb_to_app,
    aws_vpc_security_group_ingress_rule.app_from_alb,
    aws_vpc_security_group_egress_rule.app_https
  ]
}