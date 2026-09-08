#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.sh"
expected=$(cat "$DELIVERY_DIR/task-definition-arn")

# Wait for ECS, then ensure it did not settle on an older revision after rollback.
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"
actual=$(aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
  --query 'services[0].taskDefinition' --output text)
if [[ "$actual" != "$expected" ]]; then
  echo "Deployment failed or rolled back: expected $expected, found $actual" >&2
  exit 1
fi

# Confirm the application answers HTTP requests with the expected health payload.
curl --fail --silent --show-error --retry 5 --retry-connrefused \
  --retry-delay 5 --max-time 15 "$APP_URL/healthz" | jq -e '.status == "ok"'
echo "Verified $expected at $APP_URL"
