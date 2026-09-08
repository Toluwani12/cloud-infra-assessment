#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.sh"
: "${IMAGE_TAG:?Set a unique IMAGE_TAG for the tested and scanned image}"
mkdir -p "$DELIVERY_DIR"
rm -f "$DELIVERY_DIR/image-uri"

# Sign in, then upload the local image that passed the pipeline checks.
aws ecr get-login-password --region "$AWS_REGION" |
  docker login --username AWS --password-stdin "$ECR_REGISTRY"
trap 'docker logout "$ECR_REGISTRY" >/dev/null' EXIT
docker tag "assessment-app:$IMAGE_TAG" "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
docker push "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

# Save the exact image address for deploy.sh. No rebuild happens after scanning.
digest=$(aws ecr describe-images --repository-name "$ECR_REPOSITORY" \
  --image-ids "imageTag=$IMAGE_TAG" --query 'imageDetails[0].imageDigest' --output text)
[[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]] || { echo "Invalid image digest" >&2; exit 1; }
printf '%s@%s\n' "$ECR_REGISTRY/$ECR_REPOSITORY" "$digest" > "$DELIVERY_DIR/image-uri"
echo "Published $(cat "$DELIVERY_DIR/image-uri")"
