#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
case "${TF_ACTION:-plan}" in
  plan|apply) ;;
  *) echo "TF_ACTION must be plan or apply" >&2; exit 1 ;;
esac
# Plans and state stay off Git and are never uploaded as public artifacts.
trap 'rm -f ci.tfplan' EXIT
terraform init -input=false -lockfile=readonly
terraform plan -input=false -lock-timeout=120s -out=ci.tfplan
if [[ "${TF_ACTION:-plan}" == apply ]]; then
  terraform apply -input=false -lock-timeout=120s ci.tfplan
fi
