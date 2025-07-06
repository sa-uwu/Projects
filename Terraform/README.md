# 🌐 AWS NGINX Web Server Deployment using Terraform

This project provisions a complete AWS infrastructure using Terraform to deploy an NGINX web server. The architecture includes a custom VPC, public and private subnets(you can skip the pvt subnet🙂), internet gateway, route tables, security groups, and an AWS EC2 instance running NGINX 💪.

---

## 🚀 Project Overview

- Provision an isolated **VPC**
- Create **public and private subnets**
- Deploy an **EC2 instance** in the public subnet (can be moved to private sub + **ALB**)
- Install and start **NGINX**
- Attach an **Internet Gateway** and configure route tables
- Define **Security Groups** for HTTP traffic
- Output.tf to return **Public IP** and **Website URL** for ease of access

---

## 🛠️ Prerequisites
- Terraform (latest version)
- Code editor of your choice, VSCode preferrably (vs plugins do come handy😛)
- An active AWS account
- AWS CLI configured with valid credentials

---

## 📁 File Structure

```bash
.
├── main.tf                # Terraform provider and version configuration
├── provides.tf            # AWS provider configuration
├── VPC.tf                 # VPC, subnets, IGW, route tables
├── EC2.tf                 # EC2 instance and user data script
├── EC2-SG.tf              # Security group for EC2
├── output.tf              # Terraform outputs
└── README.md              # This file

```
---

## 🧑‍💻 How to Use
1. Clone this repo
```bash
git clone https://github.com/your-username/terraform-nginx-aws.git
cd terraform-nginx-aws
```

2. Initialize Terraform
```bash
terraform init
```

3. Validate the config
```bash
terraform validate
```

4. Preview the changes
```bash
terraform plan
```

5. Apply the infrastructure
```bash
terraform apply
```

6. Access the NGINX Web Server by copying the public IP or URL from the Terraform output and open it in your browser

---

## 🧹 Cleanup
 To destroy the resources created within the scope of **this project**
```bash
terraform destroy
```


---

## 📌 Notes

1. The current setup deploys EC2 in a public subnet for direct access.
2. For production, it's recommended to place EC2 in a private subnet behind an ALB.
3. The EC2 instance runs NGINX on port 80 and is open to the internet via security group.
4. You can make use of "UserData" to install updates and packages.
5. Incase you need to manually access the server, think of more aws native solutions like........ drum roll🥁
**Sesssion Manager**
6. Lastly, **Delete‼️ AWS resources** that you no longer require. 
It helps you keeps your console clean and not **wallet💰**

**Checkout this [AWS re:Post article](https://repost.aws/knowledge-center/install-ssm-agent-ec2-linux)** for more info.



## From Author ✍️

---
Just getting started with my journey of documenting both my professional and personal work.  
There’s much more to come as I continue to broaden my expertise in AWS and the IT world in general.


Stay tuned 🎧.


**Sahil Duduskar**

[LinkedIn](https://www.linkedin.com/in/sahil-duduskar-%E2%98%81%EF%B8%8F-266274225?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B2ydZuVW0SOW24I6D52ZtwA%3D%3D)













