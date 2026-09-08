resource "aws_ecs_cluster" "main" {
  name = "assessment-cluster"
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/assessment-app"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "app" {
  family                   = "assessment-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu                = "256"
  memory             = "512"
  execution_role_arn = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "public.ecr.aws/docker/library/nginx:stable-alpine"
      essential = true

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      command = [
        "/bin/sh",
        "-c",
        "sed -i 's/80;/8080;/g' /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "app"
        }
      }
    }
  ])
}