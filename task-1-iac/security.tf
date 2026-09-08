resource "aws_security_group" "alb" {
  name        = "assessment-alb"
  description = "Allow public HTTP access to the load balancer"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "assessment-alb"
  }
}

resource "aws_security_group" "app" {
  name        = "assessment-app"
  description = "Allow application access from the load balancer"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "assessment-app"
  }
}

resource "aws_vpc_security_group_ingress_rule" "public_http" {
  security_group_id = aws_security_group.alb.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_to_app" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.app.id

  from_port   = 8080
  to_port     = 8080
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "app_from_alb" {
  security_group_id            = aws_security_group.app.id
  referenced_security_group_id = aws_security_group.alb.id

  from_port   = 8080
  to_port     = 8080
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "app_https" {
  security_group_id = aws_security_group.app.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 443
  to_port     = 443
  ip_protocol = "tcp"
}