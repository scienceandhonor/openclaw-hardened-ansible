#!/usr/bin/env bash
# create-reminder.sh — schedule a one-time reminder via openclaw cron
#
# Usage: create-reminder.sh "<message>" "<time expression>"
#   <message>         Text to send when the reminder fires
#   <time expression> Anything GNU date -d understands: "in 30 minutes",
#                     "tomorrow at 9am", "2026-03-01 15:00", etc.

set -euo pipefail

# Load deployment config for TELEGRAM_USERID
[[ -f "$HOME/scripts-config.env" ]] && source "$HOME/scripts-config.env"
TELEGRAM_USERID="${TELEGRAM_USERID:-}"
if [[ -z "$TELEGRAM_USERID" ]]; then
    echo "Error: TELEGRAM_USERID not set in ~/scripts-config.env" >&2
    exit 1
fi

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 \"<message>\" \"<time expression>\"" >&2
    exit 1
fi

msg="$1"
time_expr="$2"

# Parse the time expression with GNU date (available on Ubuntu/Debian).
# Uses the system timezone; no hardcoded zone.
iso_time=$(date -d "$time_expr" --iso-8601=seconds 2>/dev/null) || {
    echo "Error: could not parse time expression: $time_expr" >&2
    exit 1
}

# Verify the scheduled time is in the future.
now_epoch=$(date +%s)
target_epoch=$(date -d "$iso_time" +%s)
if [[ "$target_epoch" -le "$now_epoch" ]]; then
    echo "Error: scheduled time '$iso_time' is in the past" >&2
    exit 1
fi

# Schedule the one-time job via the OpenClaw CLI.
# --at accepts an ISO 8601 timestamp. One-time jobs auto-remove after firing.
result=$(openclaw cron add --at "$iso_time" --message "$msg" --announce --channel telegram --to "$TELEGRAM_USERID" 2>&1) || {
    echo "Error: openclaw cron add failed: $result" >&2
    exit 1
}

# Log to reminders.md (create file if it doesn't exist).
log_file="$HOME/workspace/reminders.md"
mkdir -p "$(dirname "$log_file")"
echo "- [scheduled] $(date --iso-8601=seconds) | at $iso_time | $msg" >> "$log_file"

echo "Reminder scheduled for $iso_time"
echo "$result"
