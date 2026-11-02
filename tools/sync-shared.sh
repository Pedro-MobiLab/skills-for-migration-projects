#!/usr/bin/env bash
# Copy the shared method primer and the engagement-profile template into every
# skill, so each skill folder stays self-contained when installed on its own.
# Run after editing anything in shared/ or profiles/_template.engagement-profile.yaml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for skill in "$ROOT"/skills/*/; do
  mkdir -p "$skill/references"
  cp "$ROOT/shared/method-primer.md" "$skill/references/method-primer.md"
  cp "$ROOT/profiles/_template.engagement-profile.yaml" "$skill/references/engagement-profile.template.yaml"
  echo "synced -> $(basename "$skill")"
done
