#!/usr/bin/env bash
set -euo pipefail

checkpoint_path="${1:-/workspace/model_artifacts/beats/BEATs_iter3_plus_AS2M.pt}"
checkpoint_url='https://1drv.ms/u/s!AqeByhGUtINrgcpke6_lRSZEKD5j2Q?e=A3FpOf&download=1'
partial_path="${checkpoint_path}.part"

mkdir -p "$(dirname "$checkpoint_path")"
trap 'rm -f "$partial_path"' EXIT

curl --location --fail --retry 2 --connect-timeout 20 \
  --user-agent 'Mozilla/5.0' \
  "$checkpoint_url" \
  --output "$partial_path"

test -s "$partial_path"
mv "$partial_path" "$checkpoint_path"
trap - EXIT
sha256sum "$checkpoint_path"
