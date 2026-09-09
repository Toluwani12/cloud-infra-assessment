#!/usr/bin/env bash
# One-time IAM setup by an administrator; does not run Terraform.
set -euo pipefail
cd "$(dirname "$0")"
export AWS_REGION=eu-west-1 AWS_PAGER=""
role=assessment-terraform-ci
account=$(aws sts get-caller-identity --query Account --output text)
[[ "$account" == 151065283508 ]] || { echo "Wrong AWS account" >&2; exit 1; }
error=$(mktemp)
trap 'rm -f "$error"' EXIT
if aws iam get-role --role-name "$role" >/dev/null 2>"$error"; then
  aws iam update-assume-role-policy --role-name "$role" --policy-document file://trust.json
elif grep -q NoSuchEntity "$error"; then
  aws iam create-role --role-name "$role" --assume-role-policy-document file://trust.json >/dev/null
else
  cat "$error" >&2; exit 1
fi
for policy in policies/*.json; do
  aws iam put-role-policy --role-name "$role" \
    --policy-name "assessment-$(basename "$policy" .json)" --policy-document "file://$policy"
done
gh variable set TERRAFORM_ROLE_ARN --repo Toluwani12/cloud-infra-assessment \
  --body "arn:aws:iam::$account:role/$role"
echo "GitHub Terraform role configured. Run Terraform infrastructure -> plan on main."
