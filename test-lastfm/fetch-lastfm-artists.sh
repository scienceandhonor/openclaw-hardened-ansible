#!/bin/bash
# Local test version of fetch-lastfm-artists.sh.j2
# Credentials are read from config.env in the same directory.
# All output files (lastfm-artists.json, lastfm-last-fetch.txt, *.log) are
# written to this directory instead of the openclaw home.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$SCRIPT_DIR/config.env" ]; then
    echo "ERROR: config.env not found. Copy config.env and fill in your credentials."
    exit 1
fi

# shellcheck source=config.env
source "$SCRIPT_DIR/config.env"

if [ -z "$LASTFM_API_KEY" ] || [ "$LASTFM_API_KEY" = "your_api_key_here" ]; then
    echo "ERROR: Set LASTFM_API_KEY in config.env"
    exit 1
fi
if [ -z "$LASTFM_USERNAME" ] || [ "$LASTFM_USERNAME" = "your_lastfm_username" ]; then
    echo "ERROR: Set LASTFM_USERNAME in config.env"
    exit 1
fi

DB_FILE="$SCRIPT_DIR/lastfm-artists.json"
LOG_FILE="$SCRIPT_DIR/lastfm-artists-cron.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

FROM=1767225600  # 2026-01-01 00:00:00 UTC

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

URL="https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=${LASTFM_USERNAME}&api_key=${LASTFM_API_KEY}&format=json&limit=200&from=${FROM}"

log "Fetching recent tracks for $LASTFM_USERNAME..."

if ! curl -sf --connect-timeout 15 --max-time 60 "$URL" -o "$TMP"; then
    log "ERROR: curl failed (exit $?)"
    exit 1
fi

if [ ! -s "$TMP" ]; then
    log "ERROR: Empty response from Last.fm API"
    exit 1
fi

RESULT=$(python3 - "$TMP" "$DB_FILE" <<'PYEOF'
import json, sys

response_file = sys.argv[1]
db_path = sys.argv[2]

with open(response_file) as f:
    response = json.load(f)

if 'error' in response:
    print(f"ERROR: Last.fm API error {response['error']}: {response.get('message', '')}", file=sys.stderr)
    sys.exit(1)

tracks = response.get('recenttracks', {}).get('track', [])
if isinstance(tracks, dict):
    tracks = [tracks]

new_names = set()
for t in tracks:
    if t.get('@attr', {}).get('nowplaying'):
        continue
    name = t.get('artist', {}).get('#text', '').strip()
    if name:
        new_names.add(name)

try:
    with open(db_path) as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = []

existing_names = {a['name'] for a in existing}
added = 0
for name in new_names:
    if name not in existing_names:
        existing.append({'name': name})
        added += 1

existing.sort(key=lambda a: a['name'].lower())

with open(db_path, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

print(f"{added} new artists added, {len(existing)} total in database")
PYEOF
)
PY_EXIT=$?

if [ $PY_EXIT -ne 0 ]; then
    log "ERROR: $RESULT"
    exit 1
fi

log "$RESULT"
log "DB: $DB_FILE"
