#!/usr/bin/env bash
set -euo pipefail

if find . -type f \( -name '.env' -o -name '.env.*' -o -name '*.pem' -o -name '*.key' \) -not -path './node_modules/*' -print -quit | grep -q .; then
  echo 'Possible secret files found.' >&2
  exit 1
fi

if git grep -n -I -E '(API_KEY|SECRET|TOKEN|PASSWORD|DATABASE_URL|PRIVATE_KEY|BEGIN [A-Z ]+ KEY)' -- ':!pnpm-lock.yaml' ':!recovered-deployment/**' ':!scripts/audit-publication.sh' 2>/dev/null; then
  echo 'Review the matches above before publishing.' >&2
  exit 1
fi

echo 'Publication audit passed.'
