#!/usr/bin/env bash
# create-recurring.sh — schedule a recurring reminder via openclaw cron
#
# Usage: create-recurring.sh "<message>" "<cron expression>"
#   <message>         Text to send each time the reminder fires
#   <cron expression> Standard 5-field cron: "0 9 * * 1-5" (weekdays at 9am)

set -euo pipefail

# Load deployment config for TELEGRAM_USERID
[[ -f "$HOME/scripts-config.env" ]] && source "$HOME/scripts-config.env"
TELEGRAM_USERID="${TELEGRAM_USERID:-}"
if [[ -z "$TELEGRAM_USERID" ]]; then
    echo "Error: TELEGRAM_USERID not set in ~/scripts-config.env" >&2
    exit 1
fi

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 \"<message>\" \"<cron expression>\"" >&2
    exit 1
fi

msg="$1"
cron_expr="$2"

# Basic sanity check: cron expression should have 5 fields.
field_count=$(echo "$cron_expr" | awk '{print NF}')
if [[ "$field_count" -ne 5 ]]; then
    echo "Error: cron expression must have exactly 5 fields (got $field_count): $cron_expr" >&2
    exit 1
fi

# Schedule the recurring job via the OpenClaw CLI.
# --cron accepts a standard 5-field cron expression.
result=$(openclaw cron add --cron "$cron_expr" --message "$msg" --announce --channel telegram --to "$TELEGRAM_USERID" 2>&1) || {
    echo "Error: openclaw cron add failed: $result" >&2
    exit 1
}

# Log to reminders.md (create file if it doesn't exist).
log_file="$HOME/clawd/reminders.md"
mkdir -p "$(dirname "$log_file")"
echo "- [recurring] $(date --iso-8601=seconds) | cron '$cron_expr' | $msg" >> "$log_file"

echo "Recurring reminder scheduled: $cron_expr"
echo "$result"
