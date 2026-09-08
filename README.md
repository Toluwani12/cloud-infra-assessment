# Cloud Infrastructure Assessment

I built an AWS application with Terraform, automated its container delivery,
and wrote an HTTP health checker. I kept each task in its own folder and
recorded the implementation in incremental Git commits.

## Task 1: AWS Infrastructure

I used Terraform to create a public load balancer and two ECS Fargate tasks
in private subnets across two Availability Zones. I configured NAT gateways,
CPU scaling between two and four tasks, CloudWatch logs, resource tags, and
encrypted S3 remote state with locking.

I verified HTTP 200, two running tasks in separate zones, healthy targets,
and a scaling policy targeting 60% CPU. I have not tested CPU scale-out
under load or a full Availability Zone outage.

[Setup, architecture, and cleanup](task-1-iac/README.md)

## Task 2: Containerization and CI/CD

I built a Python application and a multi-stage, non-root Docker image.
My GitHub Actions pipeline builds, tests, and scans the image, blocks
HIGH/CRITICAL vulnerabilities, then uses OIDC to publish to ECR and deploy
the same image digest to ECS. Small scripts handle publishing, deployment,
and verification separately.

I verified a successful full pipeline run and the live Python health
response. I documented production promotion; a separate production
environment is not deployed.

[Files, commands, and deployment evidence](task-2-cicd/README.md)

## Task 3: HTTP Health Checker

I wrote a Python checker with JSON/environment configuration, expected
status checks, response timing, configurable retries and backoff, a JSON
summary, and failure exit codes. I verified eleven automated tests and a
successful check against the deployed application.

[Usage, settings, tests, and monitoring extensions](task-3-scripting/README.md)

## Costs

My AWS resources incur charges while running. I follow the Task 1 and
Task 2 cleanup instructions when the demonstration is finished.
