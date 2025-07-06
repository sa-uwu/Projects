#Creating a VPC

resource "aws_vpc" "WebServerVPC" {
    cidr_block = "10.0.0.0/16"
    tags = {
      Name = "TF-WebServerVPC"
      Project = "Terraform"
    }
  
}



#Creating a Public Subnet

resource "aws_subnet" "PublicSub1" {
    vpc_id = aws_vpc.WebServerVPC.id
    cidr_block = "10.0.1.0/24"
    tags = {
      Name = "TF-PublicSub1"
      Project = "Terraform"
    }
  
}



#Creating a Private Subnet

resource "aws_subnet" "PrivateSub1" {
    vpc_id = aws_vpc.WebServerVPC.id
    cidr_block = "10.0.2.0/24"
    tags = {
      Name = "TF-PrivateSub1"
      Project = "Terraform"
    }
  
}


#Creating an InternetGateway

resource "aws_internet_gateway" "IGW" {
    vpc_id = aws_vpc.WebServerVPC.id
    tags = {
      Name = "TF-IGW"
      Project = "Terraform"
    }
  
}


# Creating a Route Table and RouteTable Association

resource "aws_route_table" "RouteTable"{
    vpc_id = aws_vpc.WebServerVPC.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.IGW.id
    }
    tags = {
      Name = "TF-RouteTable"
      Project = "Terraform"
    }
}

resource "aws_route_table_association" "RT-Association" {
    route_table_id = aws_route_table.RouteTable.id
    subnet_id = aws_subnet.PublicSub1.id
}



