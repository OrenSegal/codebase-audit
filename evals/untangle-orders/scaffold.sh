#!/usr/bin/env bash
# A small orders app whose tests pass, with planted structural problems for untangle (ground truth in graders/result.md).
set -euo pipefail
cp -R "$(dirname "${BASH_SOURCE[0]}")/fixtures/orders/." .
git init -q
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm "orders app"
