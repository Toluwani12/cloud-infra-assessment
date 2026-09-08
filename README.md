# Cloud Infrastructure Assessment

I am building an AWS web application using Terraform.

Verified on 8 September 2026:
- Application returned HTTP 200 through the public load balancer.
- ECS reported 2 running tasks and 0 pending tasks.
- Tasks ran in separate Availability Zones: eu-west-1a and eu-west-1b.
- Both load balancer targets were healthy on port 8080.
- The main Terraform setup uses S3 remote state with native locking.

CPU scale-out under load and Availability Zone failure recovery
have not yet been tested.