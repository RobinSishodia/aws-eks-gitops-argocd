# End-to-End GitOps Deployment on AWS EKS using ArgoCD

## 📌 Overview
This project demonstrates an end-to-end DevOps workflow using AWS EKS,
Terraform, Docker, Kubernetes, Jenkins, and ArgoCD following GitOps principles.

## 🛠 Tech Stack
- AWS (EKS, EC2, IAM, VPC)
- Terraform
- Docker
- Kubernetes
- Jenkins
- ArgoCD
- Prometheus & Grafana

## 🏗 Architecture
This architecture includes AWS EKS cluster provisioned using Terraform,
CI pipeline using Jenkins, and GitOps-based continuous delivery using ArgoCD.

## 🔄 CI/CD Workflow
1. Code pushed to GitHub
2. Jenkins builds Docker image
3. Image pushed to DockerHub
4. ArgoCD syncs Kubernetes manifests
5. Application deployed to EKS

## 🚀 Implementation Steps
1. Provision AWS infrastructure using Terraform
2. Build and push Docker image
3. Configure Jenkins pipeline
4. Deploy application using Kubernetes manifests
5. Enable GitOps using ArgoCD

## 📸 Screenshots
(Add screenshots of Jenkins pipeline, ArgoCD dashboard, app running)

## 📚 Learnings
- GitOps workflow using ArgoCD
- Kubernetes deployment strategies
- Infrastructure as Code on AWS
- CI/CD automation
