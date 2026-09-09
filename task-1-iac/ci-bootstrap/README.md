# GitHub Terraform permissions

I keep infrastructure provisioning separate from the application delivery
role. This setup script creates `assessment-terraform-ci` and sets the
GitHub repository variable `TERRAFORM_ROLE_ARN`. It does not run Terraform.
An administrator must run this one-time setup after AWS login. Prerequisites
are AWS CLI, GitHub CLI authenticated with repository administration access,
and the existing GitHub OIDC provider and protected state bucket.

```bash
AWS_PROFILE=assessment-terraform bash task-1-iac/ci-bootstrap/setup-role.sh
```

The files are split by responsibility:

| File | Purpose |
|---|---|
| `trust.json` | Accept OIDC only for this repository's immutable identity on main |
| `setup-role.sh` | Create/update the role, install policies, configure GitHub |
| `policies/read.json` | Read resource configuration for Terraform refresh and plan |
| `policies/state.json` | Read/write this state key and create/delete its lock |
| `policies/network.json` | Manage networking in eu-west-1 |
| `policies/services.json` | Manage the load balancer, ECS service, and scaling |
| `policies/storage-logs.json` | Manage the named ECR repository and log group |
| `policies/iam.json` | Manage the two workload roles and existing OIDC provider |

These are provisioning permissions, not administrator access. Some network,
load-balancer, and scaling actions are region-wide; read access is broad.
This is a lab provisioning role, not a complete least-privilege production
policy. Managing workload IAM policies remains sensitive. Production needs
further resource/tag constraints, permissions boundaries, separate plan and
apply roles, and protected branches/environments with independent review.
The role cannot change its own policy through the listed IAM permissions.

I keep this CI role outside the infrastructure state so a teardown does not
remove the identity running it. Its trust provider is in the main state, so
removing that provider disables future OIDC sessions. An administrator must
remove the CI role and inline policies separately after final teardown.
For a fresh account, an administrator must also prepare the backend bucket,
OIDC provider, and required service-linked roles before this workflow runs.

Setup status: files prepared; live creation and AWS plan/apply verification
are pending a refreshed administrator login. No access keys are stored here.
