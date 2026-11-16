# GitOps on Kubernetes with ArgoCD and Jenkins

A small end-to-end GitOps pipeline: a code push is built into a Docker image by Jenkins, the new image tag is committed back to Git, and ArgoCD deploys it to Kubernetes automatically. Git is the single source of truth, and manual changes to the cluster are reverted.

Runs on a local [kind](https://kind.sigs.k8s.io/) cluster, and has also been provisioned on AWS EKS with Terraform (see [Running it on AWS EKS](#running-it-on-aws-eks-terraform)).

## How it works

```
 git push (app code)
        |
        v
  Jenkins pipeline
   1. build Docker image
   2. push image to Docker Hub (tag = build number)
   3. commit the new tag into k8s/deployment.yaml
        |
        v
  GitHub repo (source of truth)
        |
        v
  ArgoCD watches k8s/ and syncs the cluster
        |
        v
  Kubernetes runs 3 replicas of the app
```

## Stack

| Piece | Tool |
|---|---|
| App | Python / Flask |
| Container | Docker, Docker Hub |
| Orchestration | Kubernetes (kind, local) |
| CD | ArgoCD (automated sync, prune, self-heal) |
| CI | Jenkins (declarative pipeline, `Jenkinsfile`) |

## Repo layout

| Path | What it is |
|---|---|
| `app/` | Flask app, `requirements.txt`, `Dockerfile` |
| `k8s/` | Kubernetes `Deployment` and `Service` |
| `argocd-app.yaml` | ArgoCD `Application` that watches `k8s/` |
| `Jenkinsfile` | Build, push and manifest-update pipeline |
| `docs/` | Screenshots |

## What I verified

- **Self-healing:** deleting a pod, or scaling the Deployment down by hand, is undone automatically (Kubernetes restores deleted pods, ArgoCD reverts the manual scale).
- **GitOps deploy:** changing `replicas` from 2 to 3 in Git scaled the cluster with no `kubectl apply`.
- **Full loop:** editing `app/app.py` and running the Jenkins job led to a new image on Docker Hub, a Jenkins commit updating the image tag, and ArgoCD rolling out the new pods.

### ArgoCD: Healthy and Synced

![ArgoCD](docs/argocd.png)

### Jenkins: successful build

![Jenkins](docs/jenkins.png)

### The deployed app after a pipeline run

![App](docs/app.png)

## Run it locally

Prerequisites: Docker, `kubectl`, `kind`.

```bash
kind create cluster --name gitops
kubectl create namespace argocd
kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f argocd-app.yaml
```

Open ArgoCD with `kubectl port-forward svc/argocd-server -n argocd 8081:443`, and the app with `kubectl port-forward svc/gitops-demo 8080:80`.

Jenkins runs as a container (`jenkins/jenkins:lts-jdk21`) with the Docker socket mounted. It needs two credentials: `dockerhub` and `github` (a fine-grained token with Contents read/write on this repo).

## Notes and limits

- The Jenkins job is started manually; there is no webhook trigger yet.
- Jenkins runs as root with the Docker socket mounted. That is fine for a local lab, not for production.
- ArgoCD uses a self-signed certificate locally.

## Running it on AWS EKS (Terraform)

The same GitOps flow was provisioned on AWS with Terraform, verified, and then destroyed to avoid cost.

- `terraform/` builds a VPC (2 AZs, public and private subnets, one NAT gateway) and an EKS cluster (Kubernetes 1.37) with a managed node group of 2 x `c7i-flex.large`, using the community `terraform-aws-modules` vpc and eks modules.
- ArgoCD was installed on the cluster and `argocd-app.yaml` pointed it at `k8s/`. The Flask app deployed as 3 pods pulled from Docker Hub, `Synced` and `Healthy`.
- `terraform destroy` removed all 56 resources, and the cleanup was verified with the AWS CLI.

![EKS nodes, ArgoCD application and pods](docs/eks-terminal.png)
![The app served from EKS](docs/eks-app.png)
![ArgoCD on EKS showing Synced and Healthy](docs/eks-argocd.png)

### What went wrong, and the fixes

- **Free plan instance types:** the first node group failed with `InvalidParameterCombination ... not eligible for Free Tier` for `t3.medium`. I listed the allowed types with `aws ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true` and switched to `c7i-flex.large`.
- **Nodes never became ready:** version 21 of the EKS module does not install the core cluster add-ons by default, so the nodes had no pod networking. Declaring `vpc-cni`, `kube-proxy`, `coredns` and `eks-pod-identity-agent` in the module's `addons` fixed it.
- **A stuck apply:** a node group that never became ready kept Terraform waiting for hours. I added a 25-minute create timeout to the node group so a stuck build fails fast.

## Roadmap

- [x] Provision EKS with Terraform and run the same GitOps flow on AWS
- [ ] GitHub webhook to trigger Jenkins on push
