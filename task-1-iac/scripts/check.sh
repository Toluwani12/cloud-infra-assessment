#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
terraform fmt -check -recursive
terraform init -backend=false -input=false -lockfile=readonly
terraform validate
