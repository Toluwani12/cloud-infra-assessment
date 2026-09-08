resource "aws_ecr_repository" "app" {
  name                 = "assessment-app"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "assessment-app"
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}