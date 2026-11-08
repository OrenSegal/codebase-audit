#!/usr/bin/env bash
# Seed the workspace with a small app holding eight planted defects and one fence (see ANSWERS.md).
set -euo pipefail
cp -R "$(dirname "${BASH_SOURCE[0]}")/fixtures/pantry/." .
git init -q
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm "pantry app"
