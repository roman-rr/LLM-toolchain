output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "public_ip" {
  value = aws_instance.app.public_ip
}