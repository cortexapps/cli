#!/usr/bin/env bash
# Switch environment profile by patching .env with values from .env.<profile>.
#
# Profile files contain only the vars that differ per environment (e.g.,
# CORTEX_API_KEY, CORTEX_BASE_URL). All other vars in .env are left untouched.
#
# Usage:
#   ./scripts/switch-env.sh local    # switch to .env.local
#   ./scripts/switch-env.sh          # switch to .env.default (cloud workspace)
set -euo pipefail

PROFILE="${1:-default}"
PROFILE_FILE=".env.${PROFILE}"

if [ ! -f "$PROFILE_FILE" ]; then
    echo "Profile not found: $PROFILE_FILE"
    echo ""
    echo "Available profiles:"
    for f in .env.*; do
        # Skip .env.example and .env.active
        case "$f" in
            .env.example|.env.active) continue ;;
            .env.*) echo "  ${f#.env.}" ;;
        esac
    done
    exit 1
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        touch .env
    fi
fi

# Patch: for each KEY=VALUE in the profile, update or append in .env
while IFS= read -r line || [ -n "$line" ]; do
    # Skip comments and blank lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// /}" ]] && continue

    KEY=$(echo "$line" | cut -d'=' -f1)
    # Remove existing line for this key (if any), then append the new one
    grep -v "^${KEY}=" .env > .env.tmp || true
    mv .env.tmp .env
    echo "$line" >> .env
done < "$PROFILE_FILE"

# Record active profile
echo "$PROFILE" > .env.active

echo "Switched to profile: $PROFILE"
echo ""
grep -E '^(CORTEX_API_KEY|CORTEX_BASE_URL|CORTEX_APP_URL|CORTEX_TENANT_CODE)=' .env | \
    sed 's/\(CORTEX_API_KEY=\).*/\1...redacted.../'
