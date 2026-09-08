output "website_url" {
  description = "Open this address after deployment"
  value       = "http://${aws_lb.app.dns_name}"
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "service_name" {
  value = aws_ecs_service.app.name
}

output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}