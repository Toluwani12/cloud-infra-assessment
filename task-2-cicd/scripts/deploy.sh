#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.sh"

# Use the image recorded by publish.sh and the settings in our JSON file.
image=$(cat "$DELIVERY_DIR/image-uri")
[[ "$image" =~ @sha256:[a-f0-9]{64}$ ]] || { echo "Expected a digest-pinned image" >&2; exit 1; }
rm -f "$DELIVERY_DIR/task-definition-arn"
jq --arg image "$image" '.containerDefinitions[0].image = $image' \
  "$(dirname "$0")/../task-definition.json" > "$DELIVERY_DIR/task-definition.json"

# Register a new application revision and tell the existing service to use it.
revision=$(aws ecs register-task-definition \
  --cli-input-json "file://$DELIVERY_DIR/task-definition.json" \
  --query 'taskDefinition.taskDefinitionArn' --output text)
[[ "$revision" == arn:aws:ecs:* ]] || { echo "Invalid task definition ARN" >&2; exit 1; }
aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" \
  --task-definition "$revision" > /dev/null
printf '%s\n' "$revision" > "$DELIVERY_DIR/task-definition-arn"
echo "Started deployment: $revision"
