# Task 1: AWS Infrastructure with Terraform

## Overview

I initially deployed Nginx and now deliver the Task 2 Python application
behind an Application Load Balancer
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

## GitHub Terraform workflow

I now run normal Terraform checks, plans, and applies in GitHub Actions.
The earlier local provisioning established the existing state bucket and
infrastructure; it is not the ongoing deployment procedure.

1. Push a Terraform change or open a pull request. GitHub runs formatting,
   configuration validation, and script-control tests without AWS credentials.
2. After the CI role is configured, pushes to main also create an AWS plan.
3. Open **Actions → Terraform infrastructure**, open the infrastructure job,
   and review its plan. Check additions, changes, and deletions.
4. To apply, select **Run workflow**, choose **main**, and select **apply**.
   GitHub makes a fresh plan and applies that saved plan within the same run.

A fresh apply run can differ from an earlier plan if AWS state or main has
changed. I therefore recheck the selected commit and any intervening changes.
This simple workflow has no independent reviewer approval or cross-run plan
promotion. Production should add those controls. Selecting apply is an
explicit request; pushes never automatically apply infrastructure changes.

The pipeline is `.github/workflows/terraform.yml`. `scripts/check.sh` checks
formatting and validates without connecting to the backend. `scripts/run.sh`
initializes S3 state, plans, and applies only when explicitly selected.
It removes the binary plan afterward and does not upload state or plans as
artifacts. Plan text is visible in workflow logs, so sensitive variables and
outputs must be marked sensitive; public repository logs need extra care.

I use Terraform 1.14.3 and the committed AWS provider lock file. Initialization
may add a verified Linux package checksum in the temporary runner copy; it
does not request a provider version upgrade. S3 state
locking prevents concurrent writers. Infrastructure runs have their own concurrency group so they cannot cancel
pending application delivery runs. S3 locking protects Terraform state.
Before manually applying infrastructure changes, I wait for application
delivery to finish; cross-workflow deployment coordination is not automated.
GitHub concurrency is not a durable queue: newer runs can replace pending runs.

The one-time AWS role setup is documented in [ci-bootstrap](ci-bootstrap/README.md).
Until that role and `TERRAFORM_ROLE_ARN` are configured, only validation runs;
the AWS infrastructure job is explicitly skipped. This does not prove a
successful AWS plan or apply. Bootstrap state remains local and must be
preserved securely; the main state is in encrypted, versioned S3.

## CI verification

On 9 September 2026, I verified [the GitHub configuration checks](https://github.com/Toluwani12/cloud-infra-assessment/actions/runs/34353193653):
formatting, provider initialization, Terraform validation, and five script
control tests passed. The AWS infrastructure job was skipped because role
setup is pending. I have not yet verified an AWS plan/apply through this workflow.

## Verify

```bash
aws ecs wait services-stable \
  --cluster assessment-cluster \
  --services assessment-service \
  --region eu-west-1

curl --fail http://assessment-alb-784103789.eu-west-1.elb.amazonaws.com/healthz

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
- The demonstration uses unencrypted HTTP. Production needs HTTPS
  with a certificate before handling sensitive traffic.
- The public Nginx image uses a mutable tag. A digest-pinned image would
  improve reproducibility.
- With more time, I would add alarms, load tests, a controlled recovery
  exercise, and tighter provisioning permissions.

## Cleanup

NAT gateways, the load balancer, public IPv4 addresses, and Fargate tasks
incur ongoing charges.

I have not exposed a destroy option in the normal delivery workflow. For
final teardown, first disable application delivery, empty the assessment
ECR repository, and introduce a separately reviewed GitHub teardown run
that saves a `terraform plan -destroy` and applies that saved plan after
approval. That operation takes the site offline; it has not been run.
The existing workflow intentionally supports only plan and apply.

The separate state bucket remains and can still incur storage charges.
It is protected by `prevent_destroy`. Complete removal requires preserving
any needed state, deliberately removing that protection, emptying all
bucket object versions and delete markers, and destroying the bootstrap
setup. Keep the bucket while its state is still needed.