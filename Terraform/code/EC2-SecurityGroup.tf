#Creating a SecurityGroup for Ec2Instance

resource "aws_security_group" "NGINX_SG" {
    vpc_id = aws_vpc.WebServerVPC.id

    #Inbound Rules
    ingress{
        from_port = "80"
        to_port = "80"
        protocol = "tcp"                  # 'tcp' protocol is used for HTTP traffic
        cidr_blocks = ["0.0.0.0/0"]       # This allows users from anywhere (0.0.0.0/0) to access your web server via HTTP.

    }

    #Outbound Rules
    egress{
        from_port = 0
        to_port = 0
        protocol= "-1"                    # allow all protocols
        cidr_blocks = ["0.0.0.0/0"]       # Your EC2 instance can reach the internet or any other services.

    }

    tags = {
      Name = "TF-EC2_NGINX-SG"
      Project = "Terraform"
    }

  
}
