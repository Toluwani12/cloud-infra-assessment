# Task 1: AWS Infrastructure with Terraform

## Overview

I deployed an Nginx web application behind an Application Load Balancer
using ECS Fargate. Fargate runs the containers without requiring me to
manage EC2 servers. ECS Service Auto Scaling provides the assessment's
allowed equivalent to an Auto Scaling Group.

## Architecture

```text
                     Internet
                         |
              Public Load Balancer
                  /            \
          Private subnet    Private subnet
           eu-west-1a        eu-west-1b
            App task         App task
                |                |
              NAT A            NAT B
                |                |
                Internet Gateway
```

The load balancer accepts HTTP on port 80 and forwards requests to
application tasks on port 8080. Tasks have no public IP addresses and
accept application traffic only from the load balancer's security group.

Each private subnet uses a NAT gateway in its own zone for outbound
connections. Application logs are retained in CloudWatch for seven days.

## File Organization

| File | Purpose |
|---|---|
| main.tf | AWS provider and default tags |
| network.tf | VPC and subnets |
| routing.tf | Internet gateway and routing |
| nat.tf | NAT gateways and public IPs |
| security.tf | Allowed network connections |
| iam.tf | ECS execution permissions |
| loadbalancer.tf | Load balancer, listener and health checks |
| app.tf | Cluster, container definition and logs |
| service.tf | Two private application tasks |
| scaling.tf | CPU target and task-count limits |
| backend.tf | Remote state and locking |
| outputs.tf | Website URL and resource identifiers |
| bootstrap/ | Separate Terraform setup for the state bucket |

## Prerequisites and Login

Use Terraform 1.10+, AWS CLI 2.32+, Git, and an AWS account with
provisioning permissions. Commands below run from the repository root.

I used a separate IAM administrator for this learning deployment.
Production provisioning should use appropriately scoped permissions.

```bash
aws login --profile assessment-admin --region eu-west-1 --remote

aws configure set credential_process \
  "aws configure export-credentials --profile assessment-admin --format process" \
  --profile assessment-terraform

aws configure set region eu-west-1 --profile assessment-terraform

export AWS_PROFILE=assessment-terraform
export AWS_REGION=eu-west-1

aws sts get-caller-identity
```

The process profile lets Terraform obtain temporary credentials through
the AWS CLI. Credentials are not stored in the repository.

## Deploy

For a fresh setup, create the state bucket first:

```bash
terraform -chdir=task-1-iac/bootstrap init
terraform -chdir=task-1-iac/bootstrap plan -out=bootstrap.tfplan
terraform -chdir=task-1-iac/bootstrap apply bootstrap.tfplan
```

Set the bucket name in `backend.tf` to the bootstrap output.
The committed name belongs to my account; another account must update it.

Deploy the application infrastructure:

```bash
terraform -chdir=task-1-iac init -reconfigure
terraform -chdir=task-1-iac fmt -check
terraform -chdir=task-1-iac validate
terraform -chdir=task-1-iac plan -out=deploy.tfplan
terraform -chdir=task-1-iac apply deploy.tfplan
```

Review each plan before applying. Applying a saved plan executes it
without another confirmation prompt.

The main state is stored in encrypted, versioned S3 with native locking.
The bootstrap state remains local and must be preserved securely.
State and plan files are excluded from Git.

## Verify

```bash
aws ecs wait services-stable \
  --cluster assessment-cluster \
  --services assessment-service \
  --region eu-west-1

curl -I "$(terraform -chdir=task-1-iac output -raw website_url)"

aws ecs describe-services \
  --cluster assessment-cluster \
  --services assessment-service \
  --region eu-west-1 \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount}' \
  --output table
```

Verified on 8 September 2026:

- HTTP 200 through the load balancer.
- Two running tasks and zero pending tasks.
- One task in eu-west-1a and one in eu-west-1b.
- Both targets healthy on port 8080.
- Deployed CPU target of 60%.
- Successful Terraform operations using S3 state locking.

Scaling limits are configured at two to four tasks. Actual scale-out under
load and Availability Zone failure recovery have not yet been tested.

## Decisions and Trade-offs

- Two zones reduce dependence on one location.
- A NAT gateway per zone avoids a shared single-zone outbound dependency,
  but increases cost.
- The application is stateless, allowing requests to reach either task.
- HTTP is sufficient for this demonstration; production needs HTTPS
  with a certificate.
- The public Nginx image uses a mutable tag. A digest-pinned image would
  improve reproducibility.
- With more time, I would add alarms, load tests, a controlled recovery
  exercise, and tighter provisioning permissions.

## Cleanup

NAT gateways, the load balancer, public IPv4 addresses, and Fargate tasks
incur ongoing charges.

When finished, review and apply a destruction plan:

```bash
terraform -chdir=task-1-iac plan -destroy -out=destroy.tfplan
terraform -chdir=task-1-iac apply destroy.tfplan
```

This removes the application infrastructure and takes the website offline.

The separate state bucket remains and can still incur storage charges.
It is protected by `prevent_destroy`. Complete removal requires preserving
any needed state, deliberately removing that protection, emptying all
bucket object versions and delete markers, and destroying the bootstrap
setup. Keep the bucket while its state is still needed.