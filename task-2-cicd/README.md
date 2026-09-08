# Task 2: Container CI/CD

The Python app answers `/` and `/healthz` on port 8080. Three unit tests
check its welcome message, health response, and missing-page behavior.

## Follow the process

**Build → Test → Scan → Publish → Deploy → Verify**

| File | One job |
|---|---|
| `app.py` | Serve HTTP requests |
| `test_app.py` | Test application responses |
| `Dockerfile` | Package Python and the app; run as UID 10001 |
| `.github/workflows/cicd.yml` | Run the steps in order on pushes to main |
| `config.sh` | Keep shared account, region, service, and URL settings |
| `publish.sh` | Upload the checked image and record its digest |
| `task-definition.json` | Describe how ECS runs the Python container |
| `deploy.sh` | Register that definition and update the service |
| `verify.sh` | Wait for stability, detect rollback, and check `/healthz` |

The Dockerfile has a shared Alpine base, a build/test stage, and a runtime
stage. The base updates `libuuid` because the first Alpine scan found HIGH
vulnerabilities with fixes available. The final image excludes the test
file. Grype still blocks HIGH/CRITICAL findings, even without available
fixes. Medium findings may remain; a passing scan is not a permanent
security guarantee.

## Run locally

Prerequisites: Python 3, Docker with a running engine. Deployment scripts
also require Bash, AWS CLI v2 and jq. Run commands from the repository root.

```bash
python3 -m unittest discover -s task-2-cicd -v
docker build -t assessment-app:local task-2-cicd
docker run --rm --name assessment-demo --read-only --cap-drop ALL \
  -p 127.0.0.1:8080:8080 assessment-app:local
```

In a second terminal:

```bash
curl --fail http://localhost:8080/healthz
docker exec assessment-demo id
```

Expect `{"status": "ok"}` and UID 10001. Stop the container with Ctrl+C
in the first terminal. If port 8080 is already occupied by the earlier
`assessment-app` demonstration, stop that container first.

## How delivery works

Push to `main` to start the workflow, or use Actions → Run workflow on
`main`. Tests and scanning must pass before AWS credentials are requested.
The GitHub role is restricted to this repository's immutable OIDC subject
and main branch; it has scoped ECR/ECS permissions, not administrator access.
The role and registry are created by Task 1 Terraform.

The runner builds Linux AMD64 images to match the ECS task definition.
`IMAGE_TAG` combines the commit SHA, run ID, and attempt number. ECR tags
are immutable, and deployment uses the uploaded image's digest without
rebuilding it. GitHub runs only one deployment workflow at a time.

Scripts share two small generated records in ignored `.delivery/`:
`image-uri` from publish and `task-definition-arn` from deploy. The rendered
JSON is also stored there. These records are identifiers, not credentials.
For manual script use, run from the repository root, authenticate with the
Task 1 `assessment-terraform` profile, and set a unique `IMAGE_TAG` matching
an already tested and scanned local `assessment-app:$IMAGE_TAG` image:

```bash
export AWS_PROFILE=assessment-terraform
bash task-2-cicd/publish.sh
bash task-2-cicd/deploy.sh
bash task-2-cicd/verify.sh
```

`publish.sh` does not itself run the scanner: the workflow enforces that
order. The explicit JSON settings replace the earlier Nginx command and
retain the execution role, logs, resource limits, tags, and non-root user.
Terraform owns the infrastructure; the pipeline owns application revisions.
`service.tf` ignores changes to task definition and desired count so Terraform
does not undo deployments or scaling. Keep this JSON in sync when changing
CPU, memory, execution roles or logging in Terraform.

## Promote and roll back

The current `learning` environment acts as staging. After tests, scan and
staging verification pass, record the approved digest and task revision.
Production is a documented extension, not an environment created here.
Use a separate production service/state and scoped role, with a GitHub
production environment requiring approval. Deploy the SAME digest; do not
rebuild. Rescan it before promotion because new vulnerabilities may appear.
Update the explicit task-definition account/role/log/tag settings for
production and override `config.sh` defaults through environment variables.

The ECS circuit breaker can roll back an unsuccessful rollout. `verify.sh`
fails if the active revision differs from the requested revision. If the
HTTP check fails after rollout, investigate and explicitly roll back to the
previous successful task revision, then recheck service stability and HTTP.
No automatic rollback for that later HTTP failure is implemented.

## Verification and cleanup

Earlier live checks confirmed the app runs as UID 10001 and an image reached
ECR after tests and scanning. The reorganized scripts have separate local
validation; a successful full ECS deployment must be confirmed by the new
workflow run. Do not count an ECR upload alone as a deployment.

Before teardown, disable this workflow to prevent a concurrent deployment.
Delete this assessment repository's images through the ECR console, then
follow Task 1's Terraform destroy instructions. ECR deliberately refuses
repository deletion while images remain. Preserve a previous image if
rollback is still needed. Stop local test containers and remove `.delivery/`
when its records are no longer needed. The protected state bucket is managed
separately by bootstrap.
