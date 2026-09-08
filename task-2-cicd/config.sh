#!/usr/bin/env bash
# Shared settings. Existing environment variables override these defaults.
export AWS_REGION="${AWS_REGION:-eu-west-1}"
ECR_REGISTRY="${ECR_REGISTRY:-151065283508.dkr.ecr.eu-west-1.amazonaws.com}"
ECR_REPOSITORY="${ECR_REPOSITORY:-assessment-app}"
ECS_CLUSTER="${ECS_CLUSTER:-assessment-cluster}"
ECS_SERVICE="${ECS_SERVICE:-assessment-service}"
APP_URL="${APP_URL:-http://assessment-alb-784103789.eu-west-1.elb.amazonaws.com}"
DELIVERY_DIR="${DELIVERY_DIR:-.delivery}"
