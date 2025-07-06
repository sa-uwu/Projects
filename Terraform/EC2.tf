#Creating an Ec2Instance

resource "aws_instance" "Ec2_WebServer" {
    ami = "ami-0d03cb826412c6b0f"       # Replace with latest Amazon Linux AMI in the region
    instance_type = "t3.micro"          # Replace with a suitable instance type 
    subnet_id = aws_subnet.PublicSub1.id
    vpc_security_group_ids = [aws_security_group.NGINX_SG.id]
    associate_public_ip_address = true


    # User data script to install and start NGINX
    user_data = <<-EOF
                #!/bin/bash
                sudo yum install nginx -y
                sudo systemctl start nginx
            EOF

    tags = {
      Name = "TF-WebServer"
      Project = "Terraform"
    }
  
}
