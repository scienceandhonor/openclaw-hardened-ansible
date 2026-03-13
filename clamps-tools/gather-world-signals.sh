#!/usr/bin/env bash
# gather-world-signals.sh — Hourly system cron (no agent).
# Reads from existing data streams and environment, appends raw signals
# to ~/world-events/pending-signals.json for the RightClamp agent to
# translate into narrative events.
#
# Sources: time-of-day, Last.fm, X timeline, Reddit, weather (wttr.in).
# Read-only against digest pipeline files — never consumes/clears them.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/scripts-config.env" 2>/dev/null || true

STATE_DIR="${OPENCLAW_HOME:-$HOME}/world-events"
SIGNALS_FILE="${STATE_DIR}/pending-signals.json"

mkdir -p "$STATE_DIR"

# Initialise signals array if missing or corrupt
if [ ! -f "$SIGNALS_FILE" ] || ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$SIGNALS_FILE" 2>/dev/null; then
    echo '[]' > "$SIGNALS_FILE"
fi

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOUR=$(date -u +"%H" | sed 's/^0//')
WEEKDAY=$(date -u +"%A")

# Helper: atomically append a signal to the JSON array
append_signal() {
    local sig_json="$1"
    python3 -c "
import json, sys, os

path = sys.argv[1]
sig  = json.loads(sys.argv[2])

with open(path) as f:
    arr = json.load(f)
arr.append(sig)

tmp = path + '.tmp'
with open(tmp, 'w') as f:
    json.dump(arr, f, indent=2)
os.replace(tmp, path)
" "$SIGNALS_FILE" "$sig_json"
}

# ── Time-of-day signal ──────────────────────────────────────────────
phase="day"
if   [ "$HOUR" -ge 5  ] && [ "$HOUR" -lt 8  ]; then phase="dawn"
elif [ "$HOUR" -ge 8  ] && [ "$HOUR" -lt 12 ]; then phase="morning"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 14 ]; then phase="noon"
elif [ "$HOUR" -ge 14 ] && [ "$HOUR" -lt 17 ]; then phase="afternoon"
elif [ "$HOUR" -ge 17 ] && [ "$HOUR" -lt 20 ]; then phase="dusk"
elif [ "$HOUR" -ge 20 ] && [ "$HOUR" -lt 23 ]; then phase="evening"
else phase="midnight"
fi

append_signal "{\"type\":\"time\",\"data\":{\"hour\":$HOUR,\"phase\":\"$phase\",\"weekday\":\"$WEEKDAY\"},\"ts\":\"$NOW_ISO\"}"

# ── Last.fm signal (if artist data exists) ───────────────────────────
LASTFM_FILE="${OPENCLAW_HOME:-$HOME}/.openclaw/lastfm-artists.json"
if [ -f "$LASTFM_FILE" ]; then
    # Pick the most recently added artist (last entry)
    artist_json=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    artists = json.load(f)
if artists:
    a = artists[-1] if isinstance(artists, list) else {}
    name = a.get('name', a.get('artist', ''))
    if name:
        print(json.dumps({'type':'music','data':{'artist':name},'ts':sys.argv[2]}))
" "$LASTFM_FILE" "$NOW_ISO" 2>/dev/null)
    if [ -n "$artist_json" ]; then
        append_signal "$artist_json"
    fi
fi

# ── X timeline signal (read-only peek at undigested) ─────────────────
XURL_UNDIGESTED="${OPENCLAW_HOME:-$HOME}/timeline-state/undigested.json"
if [ -f "$XURL_UNDIGESTED" ]; then
    topic_json=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    posts = json.load(f)
if posts and isinstance(posts, list) and len(posts) > 0:
    # Pick the first post's text (truncated)
    text = posts[0].get('text', posts[0].get('content', ''))[:120]
    if text:
        print(json.dumps({'type':'social','data':{'source':'xurl','topic':text},'ts':sys.argv[2]}))
" "$XURL_UNDIGESTED" "$NOW_ISO" 2>/dev/null)
    if [ -n "$topic_json" ]; then
        append_signal "$topic_json"
    fi
fi

# ── Reddit signal (read-only peek at undigested) ─────────────────────
REDDIT_UNDIGESTED="${OPENCLAW_HOME:-$HOME}/reddit-state/undigested.json"
if [ -f "$REDDIT_UNDIGESTED" ]; then
    reddit_json=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    posts = json.load(f)
if posts and isinstance(posts, list) and len(posts) > 0:
    title = posts[0].get('title', '')[:120]
    sub   = posts[0].get('subreddit', '')
    if title:
        print(json.dumps({'type':'social','data':{'source':'reddit','subreddit':sub,'topic':title},'ts':sys.argv[2]}))
" "$REDDIT_UNDIGESTED" "$NOW_ISO" 2>/dev/null)
    if [ -n "$reddit_json" ]; then
        append_signal "$reddit_json"
    fi
fi

# ── Weather signal (wttr.in, no API key needed) ──────────────────────
weather_json=$(curl -sf --connect-timeout 5 --max-time 10 "https://wttr.in/?format=j1" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    cur = data['current_condition'][0]
    cond = cur.get('weatherDesc', [{}])[0].get('value', 'unknown')
    temp = cur.get('temp_C', '?')
    wind = cur.get('windspeedKmph', '0')
    print(json.dumps({'type':'weather','data':{'condition':cond,'temp_c':int(temp),'wind_kmh':int(wind)},'ts':sys.argv[1]}))
except Exception:
    pass
" "$NOW_ISO" 2>/dev/null || true)
if [ -n "$weather_json" ]; then
    append_signal "$weather_json"
fi

echo "ok: signals gathered at $NOW_ISO"
