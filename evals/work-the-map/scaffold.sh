#!/usr/bin/env bash
# A webhook app with a finished audit on disk: HANDOFF.md, REPORT.md, a red repro, and a three-ticket map in .scratch/.
set -euo pipefail
cp -R "$(dirname "${BASH_SOURCE[0]}")/fixtures/app/." .
git init -q
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm "webhook app"
