output "instance_public_ip" {
    description = "this return ec2 intances public ip "
    value = aws_instance.Ec2_WebServer.public_ip
  
}

output "instance_url" {
    value = "https://${aws_instance.Ec2_WebServer.public_ip}"
  
}
