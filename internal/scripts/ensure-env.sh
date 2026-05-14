#!/usr/bin/env bash
# Check for required env vars, prompt for missing ones, append to .env.
# Each argument is "NAME|Label|Help text".
#
# Usage:
#   ./scripts/ensure-env.sh \
#       "CORTEX_API_KEY|Cortex API key|Get from Cortex Settings > API Keys." \
#       "CORTEX_BASE_URL|Cortex API base URL|Defaults to https://api.getcortexapp.com."
set -euo pipefail

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        touch .env
    fi
fi

# Source current .env values
set -a
source .env
set +a

# Parse var declarations and find missing ones
MISSING_NAMES=()
MISSING_LABELS=()
MISSING_HELPS=()
for decl in "$@"; do
    NAME=$(echo "$decl" | cut -d'|' -f1)
    LABEL=$(echo "$decl" | cut -d'|' -f2)
    HELP=$(echo "$decl" | cut -d'|' -f3)
    VAL="${!NAME:-}"
    if [ -z "$VAL" ]; then
        MISSING_NAMES+=("$NAME")
        MISSING_LABELS+=("$LABEL")
        MISSING_HELPS+=("$HELP")
    fi
done

if [ ${#MISSING_NAMES[@]} -eq 0 ]; then
    exit 0
fi

echo ""
echo "Missing ${#MISSING_NAMES[@]} required variable(s): ${MISSING_NAMES[*]}"
echo ""

for i in "${!MISSING_NAMES[@]}"; do
    NAME="${MISSING_NAMES[$i]}"
    LABEL="${MISSING_LABELS[$i]}"
    HELP="${MISSING_HELPS[$i]}"

    echo "$NAME ($LABEL)"
    echo "  $HELP"
    while true; do
        printf ": "
        read -r VALUE
        if [ -n "$VALUE" ]; then
            echo "$NAME=\"$VALUE\"" >> .env
            export "$NAME=$VALUE"
            echo ""
            break
        fi
        echo "  Value cannot be empty. Try again."
    done
done

echo "All variables set."
echo ""
