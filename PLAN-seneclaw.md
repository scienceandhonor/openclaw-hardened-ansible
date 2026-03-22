# Seneclaw: Stoic Coach Subagent

## Context

The openclaw instance already sends a fire-and-forget daily stoic quote (`job-daily-stoic`, 07:00 UTC). The user wants a dedicated coaching subagent that uses the daily theme as a seed for proactive Socratic coaching throughout the day — questions, follow-ups, nudges — building a progressive understanding of the user's stoic practice over time via memory and workspace state.

## Name: Seneclaw

(Seneca + Claw) — concise, phonetically clean, works as a bot username and agent ID.

Runner-ups: Epicteclaws, Marcus Clawrelius (funniest but too long), Pinchictetus (sounds medical), Clawsippus (too obscure), Zeno of Clawtium (too wordy), Dioclawgenes (Cynic, not Stoic).

## Model: Claude Sonnet 4.6

**Why Sonnet over alternatives:**
- **M2.7**: Untested for nuanced philosophical coaching with sustained memory. Risk of shallow output. Keeps single-provider simplicity but that's not worth the quality gamble for a coaching agent.
- **Opus 4.6**: Best philosophical depth but ~10x Sonnet cost. Overkill for 1-4 sentence coaching nudges sent 3-4x daily. Reserve for special occasions (the weekly summary doesn't justify the permanent cost).
- **Sonnet 4.6**: Strong philosophical reasoning, good emotional intelligence, excellent at Socratic questioning. ~$0.72/month at 4 daily sessions x ~2K input tokens. Already wired as secondary provider via `anthropic_api_key`.

**Dependency**: Requires `anthropic_api_key` to be set. Template falls back to primary provider model if absent, but deploy script should warn.

## Proactive Contact Strategy

**Fixed cron windows + agent-side intelligence.**

OpenClaw cron only supports fixed schedules, but the agent can stay silent by not calling `openclaw message send`. All Seneclaw jobs use `delivery: {mode: none}` — the job-level announce delivery is disabled. The agent is the sole sender: it calls `openclaw message send --channel telegram --to <USER_ID>` explicitly when it decides to speak, and produces no output (and sends nothing) when the silence condition is met. This is the *gated announce* pattern — `delivery: announce` would forward the agent's output unconditionally, breaking all silence conditions.

Each job prompt includes explicit silence conditions ("output NOTHING if the human hasn't responded today"). A non-responsive user receives at most 1 message/day (morning seed) + 1/week (Sunday review).

Over time, semantic memory accumulates patterns ("user responds to midday messages on Tuesdays but never on Mondays") and the agent naturally adapts. No code change needed — this emerges from memory and judgment.

**Schedule (UTC, staggered against existing jobs):**

| Job | Cron | UTC | Silence condition |
|-----|------|-----|-------------------|
| Theme capture (system cron) | `55 6 * * *` | 06:55 | N/A (runs before daily quote) |
| Morning seed | `20 7 * * *` | 07:20 | Skip if sent <20h ago |
| Midday check-in | `0 12 * * *` | 12:00 | Skip if no response to morning |
| Evening reflection | `30 19 * * *` | 19:30 | Skip if zero engagement today |
| Weekly progress (Sun) | `0 10 * * 0` | 10:00 | Always send; update USER_PROGRESS.md |

**Collision avoidance**: Morning seed at 07:20 is 5 min after xurl digest (07:15), 20 min after daily stoic quote (07:00). Evening at 19:30 clears feature-tips (19:00 Fri only).

## Cross-Agent Theme Sharing

Mirrors the split-pipeline pattern (system cron writes state, agent reads state):

1. **System cron** at 06:55 UTC runs `capture-stoic-theme.sh` (new clamps-tools script)
2. Script runs `daily-stoic.py`, writes theme to `~/stoic-state/daily-theme.json`:
   ```json
   {"date": "2026-03-21", "theme": "...", "source": "Marcus Aurelius, Meditations V.20"}
   ```
3. All Seneclaw cron jobs read `daily-theme.json` as context
4. Existing `job-daily-stoic` unchanged (continues delivering quote via main agent/PincerMove)

## Workspace Files

**Directory**: `roles/tier2-setup/files/workspace-seneclaw/` — deployed with `force: false`

### AGENTS.md
Operating instructions: read daily-theme.json, search memory before every message, connect theme to user's specific life, 1-4 sentences max, output nothing when appropriate. Tracks tools (`read`, `write`, `exec` — denies `browser`, `process`, `edit`, `apply_patch`, `gateway`, `canvas`). Instructs agent to update USER_PROGRESS.md after meaningful exchanges.

### SOUL.md
Personality: warm coach, not oracle. Socratic over didactic. Curious — asks more than tells. Grounds abstract principles in concrete daily moments. Gently persistent (revisits threads across days). Honest about limits (not a therapist). Brief (text-from-a-friend feel). Anti-patterns: no quote-bombing (1 reference/message max), no moralizing, no "performing wisdom", no repeating itself.

### PHILOSOPHY.md
Reference card: Four Virtues, key practices (dichotomy of control, negative visualisation, view from above, memento mori, evening review, morning preparation, amor fati), source authors. Seeds for coaching, not scripts.

### USER_PROGRESS.md
Template with sections for Patterns (response times, engagement days), Principles That Connect, Life Context, Session Log. Agent updates this over time; `force: false` preserves it across re-deploys.

## Infrastructure Changes

### 1. `deploy-tier2.sh`
- New flag: `--stoic-telegram-bottoken TOKEN`
- Validation: require `--telegram-userid` when stoic bot token is set
- Extra-vars: `sys.argv[26]` = `stoic_telegram_bottoken`
- Status display block
- Help text

### 2. `roles/tier2-setup/templates/openclaw.json.j2`
- **Agent entry** in `agents.list` (after Sociaclamps, ~line 295):
  ```json
  {
    "id": "seneclaw", "name": "Seneclaw",
    "workspace": "{{ openclaw_home }}/workspace-seneclaw",
    "model": { "primary": "anthropic/claude-sonnet-4-6", "fallbacks": [] },
    "tools": { "deny": ["browser", "process", "edit", "apply_patch", "gateway", "canvas"] }
  }
  ```
  Model falls back to `{{ provider }}/{{ llm_model }}` if `anthropic_api_key` not set.
- **Telegram account**: `"seneclaw": { "name": "Seneclaw", "botToken": "{{ stoic_telegram_bottoken }}" }`
- **Binding**: `{ "agentId": "seneclaw", "match": { "channel": "telegram", "accountId": "seneclaw" } }`
- **Gating**: `stoic_telegram_bottoken | default('') | length > 0`

### 3. `roles/tier2-setup/tasks/install.yml`
- **Phase 3**: Create `~/workspace-seneclaw/`, `~/workspace-seneclaw/memory/`, `~/stoic-state/` directories
- **Phase 3**: Deploy workspace files (AGENTS.md, SOUL.md, PHILOSOPHY.md, USER_PROGRESS.md) with `force: false`
- **Phase 9q** (new): Python shell task managing 4 cron jobs (`job-stoic-morning`, `job-stoic-midday`, `job-stoic-evening`, `job-stoic-weekly`) — all with `agentId: seneclaw`, `delivery: {mode: none}` (gated announce: agent calls `openclaw message send` explicitly; silence conditions produce no output and no Telegram message)
- **System cron**: `capture-stoic-theme.sh` at `55 6 * * *`

### 4. `CLAUDE.md`
- Add Seneclaw convention block (gating, workspace, cron, theme sharing)
- Update extra-vars: `sys.argv[26]` = `stoic_telegram_bottoken`
- Add CLI example with `--stoic-telegram-bottoken`

### 5. clamps-tools (scripts repo)
- New: `capture-stoic-theme.sh` — runs `daily-stoic.py`, writes `~/stoic-state/daily-theme.json`

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| **Preachiness** | SOUL.md forbids quote-bombing, moralizing, performing wisdom. Max 1 reference/message. Socratic questioning by default. |
| **Timing fatigue** | 3/4 daily jobs have explicit silence conditions. Non-responsive user gets max 1 msg/day + 1/week. |
| **Shallow coaching** | Agent searches memory before every message, connects to user's specific life. Weekly progress note forces synthesis. USER_PROGRESS.md builds longitudinal understanding. |
| **Cold start** | Morning seed falls back to posing theme as a question. First few days are generic; each response enriches memory. Sunday review provides first synthesis. |
| **Memory flooding** | Isolated sessions with inherited compaction settings. Semantic memory (Gemini embeddings) enables relevant retrieval without context bloat. |
| **Cross-agent interference** | Bindings route each bot's messages exclusively. Schedule staggered with 5+ min gaps. Separate Telegram sender identity. |
| **Cost creep** | Sonnet 4.6 at ~$0.72/month. Silence conditions reduce actual invocations. |

## Verification

1. `ansible-playbook playbook-tier2.yml --syntax-check` passes
2. Deploy with `--stoic-telegram-bottoken <TOKEN>` to a test host
3. Verify `openclaw.json` contains Seneclaw agent entry, telegram account, and binding
4. Verify `~/workspace-seneclaw/` contains all 4 files
5. Verify `~/.openclaw/cron/jobs.json` contains 4 `job-stoic-*` entries with `agentId: seneclaw`
6. Verify system crontab contains `capture-stoic-theme.sh` at 06:55
7. Message the Seneclaw bot on Telegram — should route to Seneclaw agent only
8. Wait for 07:20 UTC — verify morning seed message arrives
9. Re-deploy without `--stoic-telegram-bottoken` — verify all Seneclaw config is absent
