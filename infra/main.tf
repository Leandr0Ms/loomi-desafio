terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  required_version = ">= 1.6.0"
}

provider "aws" {
  region = "us-east-1"
}

# 1 Gerar uma chave SSH local
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# 2 Registrar a chave pública na AWS como Key Pair
resource "aws_key_pair" "ec2_key" {
  key_name   = "terraform-ec2-key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

# 3 Security Group permitindo SSH 
resource "aws_security_group" "ssh_sg" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
  description = "Allow HTTPS"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4 Instância EC2
resource "aws_instance" "vm" {
  ami                    = "ami-0fc5d935ebf8bc3bc"
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.ec2_key.key_name
  vpc_security_group_ids = [aws_security_group.ssh_sg.id]

  tags = {
    Name = "desafio-vm"
  }
}

# 5 Outputs: IP público e chave privada
output "public_ip" {
  description = "IP público da instância"
  value       = aws_instance.vm.public_ip
}

output "ssh_private_key_pem" {
  description = "Chave privada para acessar a instância"
  value       = tls_private_key.ssh_key.private_key_pem
  sensitive   = true
}
