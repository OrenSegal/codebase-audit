#!/usr/bin/env bash
# A two-package monorepo past the sequential threshold: 3 planted defects plus 200 generated filler modules.
set -euo pipefail
cp -R "$(dirname "${BASH_SOURCE[0]}")/fixtures/repo/." .
for pkg in app api; do
  mkdir -p "packages/$pkg/src/util"
  for i in $(seq 1 100); do
    printf 'export function scale%s(n: number): number {\n  return n * %s + 1;\n}\n' "$i" "$i" > "packages/$pkg/src/util/scale$i.ts"
  done
done
git init -q
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm "monorepo"
