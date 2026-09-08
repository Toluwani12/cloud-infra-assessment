# Cloud Infrastructure Assessment

My practical assessment covering AWS infrastructure, container CI/CD,
and operational scripting.

## Task 1: AWS Infrastructure

Built with Terraform and ECS Fargate:

- Public load balancer serving an Nginx web application.
- Two application tasks in private subnets across two Availability Zones.
- CPU-based scaling configured between two and four tasks.
- NAT gateways for outbound connectivity.
- CloudWatch logs and encrypted S3 state with locking.
- Project, environment, and owner tags on supported resources.

Verified: HTTP 200, two running tasks in different zones, healthy load
balancer targets, and a scaling policy targeting 60% CPU usage.

See [Task 1 documentation](task-1-iac/README.md) for architecture,
deployment, verification, and cleanup.

## Task 2: Containerization and CI/CD

A non-root Python image with tests, a HIGH/CRITICAL vulnerability gate,
OIDC authentication, and separate publish, deploy, and verify scripts.
See [Task 2 documentation](task-2-cicd/README.md) for the process and setup.

## Remaining Work

- Task 3: HTTP health-check script.

## Costs

The deployed AWS resources incur ongoing charges. Follow the Task 1
cleanup instructions when the demonstration is finished.
