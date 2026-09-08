resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"

  tags = {
    Name = "nat-ip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "main" {
  count = 2

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  depends_on = [aws_internet_gateway.main]

  tags = {
    Name = "nat-${count.index + 1}"
  }
}