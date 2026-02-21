# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Ansible deployment for hardened OpenClaw AI agents in two tiers:

- **Tier 2** — Lightweight direct-host deployment. OpenClaw runs as a systemd service (no containers). Direct LLM provider routing. TLS via Tailscale Serve. Debian/Ubuntu only.
- **Tier 3** — Full container stack with rootless Podman, egress filtering via Squid, and credential brokering via LiteLLM. Arch Linux or Debian/Ubuntu.

## Commands

### Tier 3 Deployment (containers, full stack)
```bash
# Interactive deploy (prompts for IP, provider, API keys)
./deploy.sh

# CLI-driven deploy
./deploy.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY>

# AWS/cloud with SSH key
./deploy.sh --target <IP> --ssh-user ubuntu --ssh-key ~/key.pem --provider ollama --model "deepseek-r1:8b" --url "http://10.100.1.25:11434"
```

### Tier 2 Deployment (direct host, no containers)
```bash
# Interactive deploy
./deploy-tier2.sh

# CLI-driven deploy
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY>

# With Ollama (local or remote)
./deploy-tier2.sh -t <IP> -p ollama -m llama3 -u http://localhost:11434

# With SSH key
./deploy-tier2.sh --target <IP> --ssh-user ubuntu --ssh-key ~/key.pem --provider openai -m gpt-4o -k <API_KEY>

# With OpenAI-compatible provider (e.g. MiniMax)
./deploy-tier2.sh -t <IP> -p openai_compatible -m MiniMax-M2.5 -u https://api.minimax.io/v1 -k <API_KEY>

# With Telegram channel
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY> \
  --telegram-userid <INTEGER_USER_ID> --telegram-bottoken <BOT_TOKEN>

# With Last.fm artist sync (hourly cron, builds lastfm-artists.json)
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY> \
  --lastfm-user <LASTFM_USERNAME> --lastfm-key <LASTFM_API_KEY>

# With scripts repo (clones clamps-tools, sets up deploy key + daily pull)
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY> \
  --scripts-repo user/clamps-tools
```

> **Bootstrapping sequence for `--scripts-repo`:** On first deploy Ansible generates an
> ed25519 deploy key at `~openclaw/.ssh/openclaw-scripts-deploy`, displays the public key,
> and pauses. Add it as a read-only deploy key in GitHub (repo → Settings → Deploy keys)
> then press Enter to continue. Subsequent re-runs skip key generation and pause.

### Maintenance
```bash
# Update egress allowlist (edit roles/tier3-setup/templates/allowlist.txt.j2 first)
./update-allowlist.sh -t <IP> --ssh-user <USER> --ask-pass

# Install Ansible dependencies
ansible-galaxy collection install -r requirements.yml
```

### Ansible syntax check
```bash
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook-tier2.yml --syntax-check
```

## Architecture

### Playbook Structure
Both playbooks share the same 3-play structure: (1) check for existing installation identity on remote, (2) local key/hostname generation using EFF wordlist, (3) call the appropriate role for deployment. Tier 2 skips SSL cert generation — Tailscale Serve handles TLS.

### Tier 2 Architecture (`playbook-tier2.yml` → `roles/tier2-setup/`)
OpenClaw runs as a plain systemd service under the `openclaw` user. No containers, no Podman, no LiteLLM. Provider credentials are configured directly in `openclaw.json`. **Debian/Ubuntu only.**

#### Task Flow (roles/tier2-setup/tasks/)
- `main.yml` — OS detection (Debian/Ubuntu only), includes other task files in order: `debian-system.yml` → `install.yml` → `security.yml`
- `debian-system.yml` — Package install, user creation, Tailscale auth
- `install.yml` — Node.js 22 via NodeSource (with version guard), openclaw npm install, directory structure, gateway token generation, systemd service, doctor fix, health check, **CLI device pairing bootstrap**, Tailscale Serve HTTPS, scripts repo SSH deploy key + clone/pull, `scripts-config.env` render, cron jobs (daily pull, weekly audit, hourly Last.fm sync)
- `security.yml` — UFW firewall rules, Fail2Ban, SSH hardening. Runs **last** so a failed install does not lock out root SSH.

#### Task Order Note
`security.yml` intentionally runs after `install.yml`. Running it earlier would disable root SSH (`PermitRootLogin prohibit-password`) before openclaw is installed, making the playbook impossible to re-run on failure without console access.

### Tier 3 Architecture (`playbook.yml` → `roles/tier3-setup/`)
Full container stack with rootless Podman. **Arch Linux or Debian/Ubuntu.**

#### Task Flow (roles/tier3-setup/tasks/)
- `main.yml` — OS detection (Arch vs Debian/Ubuntu), sysctl kernel limits, includes other task files
- `arch-system.yml` / `debian-system.yml` — OS-specific package install, user creation, rootless Podman setup, Tailscale auth
- `security.yml` — UFW firewall rules, Fail2Ban, SSH hardening
- `docker-deploy.yml` — Template rendering, secret generation/persistence, Podman image build, container startup, health checks, device pairing, Tailscale Serve config

#### Container Stack (deployed via Podman Compose)
- **OpenClaw Agent** — Node.js 22-Alpine AI agent runtime, exposed on port 18789 (HTTPS)
- **LiteLLM** — Credential broker + model spoofing proxy on port 4000 (internal only)
- **Squid** — Domain allowlist egress proxy on port 3128 (internal only)

#### Network Isolation
Two Podman networks: `openclaw-internal` (agent ↔ LiteLLM ↔ Squid) and `openclaw-external` (Squid-only outbound). Only port 18789 is host-bound. All container egress routes through Squid's domain allowlist.

### Secret Management
Tier 3: Gateway token and LiteLLM master key are generated on first deploy and persisted in the remote `.env` file. Subsequent runs detect and reuse existing secrets.
Tier 2: Gateway token generated with `openssl rand -hex 24` (must be 48-char hex — openclaw rejects base64 tokens at connection time). Persisted to `~/.openclaw/gateway.token`. Re-runs reuse the existing token. Provider API key written directly to `openclaw.json` by the template. Scripts repo credentials (Last.fm key, Brave key, `OPENCLAW_HOME`) are rendered into `~/scripts-config.env` (mode 0600) by Ansible — never committed to the scripts repo.

## Development Conventions

- **Rootless Podman (Tier 3):** Always use `become: true` with `become_user: "{{ openclaw_user }}"` for Podman tasks.
- **Template indentation:** For YAML templates (especially `litellm-config.yaml.j2`), keep Jinja2 control tags (`{% if %}`) at column 0 to prevent indentation errors in rendered output.
- **LiteLLM model mapping (Tier 3):** Model IDs in `litellm-config.yaml.j2` enable spoofing — a model named `claude-sonnet-4-5` can be backed by any provider.
- **Tier 2 provider config:** Provider/model/URL/key are injected directly into `openclaw.json.j2` via Jinja2 conditionals — no LiteLLM intermediary.
- **Tier 2 extra-vars format:** `deploy-tier2.sh` passes all variables as a JSON string via `python3 -c "import json,sys; print(json.dumps({...}))"`. Do not revert to the `key='$VALUE'` shell-quoting format — bot tokens contain colons which survive shlex but can corrupt YAML parsing, and the single quotes end up as literal characters in the rendered JSON. Current positional args: `sys.argv[1..10]` = `llm_provider`, `llm_model`, `llm_url`, `llm_key`, `telegram_userid`, `telegram_bottoken`, `brave_key`, `lastfm_api_key`, `lastfm_username`, `scripts_repo_slug`.
- **Scripts repo idempotency:** Phase 9a tasks that generate the deploy key and pause are all gated on `not deploy_key_stat.stat.exists`. Re-runs skip straight to pull + env render. Phase 9c clone/pull tasks are additionally gated on `scripts_repo_slug | default('') | length > 0` so deploys without `--scripts-repo` skip them cleanly.
- **Commit style:** Use conventional commits with scope, e.g. `fix(litellm):`, `feat(tier2):`, `security(ssh):`.

## openclaw.json Schema Notes (Tier 2)

Hard-won constraints from live deployment — openclaw doctor/validator enforces these:

- **`gateway.bind`** — Valid values are keywords (`"loopback"`, `"lan"`, etc.), not IP strings. `"lo"` and `"127.0.0.1"` are rejected with schema errors. Use `"loopback"` for tier 2.
- **`gateway.auth.token`** — Must be a 48-char hex string (`openssl rand -hex 24`). Base64 tokens are silently rejected at WebSocket connection time with code 4008.
- **`gateway.remote.token` / `gateway.remote.url`** — Client-side config for the CLI to connect to a remote gateway. Set these to allow CLI commands to authenticate without device pairing prompts.
- **`models.providers.<provider>.api`** — Required field for all providers except ollama. Valid values: `"anthropic-messages"`, `"openai-completions"`, `"openai-responses"`. Omitting it causes `"No API provider registered for api: undefined"` crash on the first message.
- **`models.providers.<provider>.baseUrl`** — Required field for anthropic and openai providers. Omitting it causes schema validation failure on startup.
- **`models.providers.<provider>.models`** — Required array for anthropic and openai providers. Must include at least the configured model.
- **`agents.defaults.model.primary` format** — Must use the JSON provider key, not the deploy-time variable name. The `openai_compatible` deploy param registers the provider as `"openai"` in the JSON, so the model reference must be `openai/<model>`, not `openai_compatible/<model>`. The template handles this with a Jinja2 ternary on line 110.
- **`channels.discord.dmPolicy`** — Correct field name. `channels.discord.dm.policy` is the old format; openclaw doctor migrates it automatically but the template should use the new form to avoid constant migration noise.
- **`channels.telegram.configWrites`** — Must be `false`. When `true`, chat messages can modify agent config, which is unsafe with prompt injection risk.
- **Telegram requires both `userid` and `bottoken`** — The template condition checks both. If only one is set, the block falls back to `{ "dmPolicy": "pairing" }`. Passing only one via CLI flags is caught by validation in `deploy-tier2.sh` before the playbook runs.
- **Semantic memory** — openclaw auto-detects embedding providers (OpenAI, Gemini, Voyage, or local GGUF model) and falls back to BM25-only if none are available. Do not explicitly disable it.

## openclaw Device Pairing (Tier 2 Headless Bootstrap)

openclaw has two separate auth layers that are easy to conflate:

1. **Gateway auth token** (`gateway.auth.token`) — Authenticates the browser dashboard WebSocket (controlUI). Set `gateway.remote.token` client-side for the CLI to use this token.
2. **Device pairing** — Separate per-device asymmetric key challenge. Required for CLI connections regardless of gateway token. `dangerouslyDisableDeviceAuth` only bypasses this for the controlUI, not the CLI.

**`OPENCLAW_GATEWAY_TOKEN` env var does not bypass device pairing for the CLI.** It is only for the agent API, not the control plane WebSocket.

**Headless bootstrap flow** (automated in `install.yml` Phase 7b):
1. Delete `~/.openclaw/identity/device.json` if it exists — this is critical. If a stale identity from a previous deploy is present, the CLI detects it and generates a `clientId: "gateway-client"` repair entry instead of a `clientId: "cli"` pending entry, which the bootstrap cannot approve.
2. Run any CLI command — it fails but generates a fresh `identity/device.json` (Ed25519 key pair) and writes a `clientId: "cli"` pending entry to `~/.openclaw/devices/pending.json`
3. Move the CLI's pending entry into `~/.openclaw/devices/paired.json` (keyed by `deviceId`, drop `requestId`, add `pairedAt`)
4. Restart the gateway — it reads `paired.json` on startup and trusts the CLI's public key
5. CLI connects using private key challenge from `identity/device.json`

Browser pairing is done manually post-deploy: open the dashboard URL from `openclaw dashboard --no-open` via SSH tunnel, the browser submits a pending request, approve with `openclaw nodes approve <requestId>` from the now-working CLI.

## openclaw doctor --fix and the User-Level Service Conflict

`openclaw doctor --fix` registers a user-level systemd service (`openclaw-gateway.service`) as part of self-repair. This is harmless unless `loginctl enable-linger <user>` is also active — at that point the user service starts automatically and fights the system service for port 18789, producing a ~20-second restart loop:

```
Port 18789 is already in use.
Gateway service status unknown; if supervised, stop it first.
Or: systemctl --user stop openclaw-gateway.service
```

The playbook defends against this by explicitly stopping and removing user-level service files after every `doctor --fix` run (Phase 6 cleanup in `install.yml`). If `openclaw doctor` is run manually and linger is enabled, fix it with:

```bash
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/$(id -u openclaw) \
  systemctl --user disable --now openclaw-gateway.service
sudo rm -f /home/openclaw/.config/systemd/user/openclaw-gateway.service
loginctl disable-linger openclaw  # optional; system service doesn't need it
```

## Key Files

### Tier 2
- `deploy-tier2.sh` — Interactive/CLI deployment wrapper for tier 2
- `playbook-tier2.yml` — Tier 2 playbook (identity check, key gen, tier2-setup role)
- `roles/tier2-setup/tasks/install.yml` — Main install logic (Node.js, openclaw, systemd, Tailscale Serve)
- `roles/tier2-setup/templates/openclaw.json.j2` — Agent config with direct provider routing
- `roles/tier2-setup/templates/tools.yaml.j2` — Shell allowlist and filesystem permissions
- `roles/tier2-setup/templates/mcp.json.j2` — MCP server config (memory server only)
- `roles/tier2-setup/templates/exec-approvals.json.j2` — Approved binary paths
- `roles/tier2-setup/templates/scripts-config.env.j2` — Environment file for scripts repo (rendered with secrets; never committed to scripts repo)

### Tier 3
- `deploy.sh` — Interactive/CLI deployment wrapper for tier 3
- `playbook.yml` — Tier 3 playbook defining variables and role inclusion
- `roles/tier3-setup/templates/docker-compose.yml.j2` — Container stack definition
- `roles/tier3-setup/templates/openclaw.json.j2` — Primary OpenClaw agent configuration
- `roles/tier3-setup/templates/litellm-config.yaml.j2` — LLM provider routing and model mapping
- `roles/tier3-setup/templates/allowlist.txt.j2` — Egress domain whitelist (edit this to add allowed domains)
- `roles/tier3-setup/tasks/docker-deploy.yml` — Container deployment logic (largest task file)

## Dependencies

- **Ansible collection:** `community.general` (for pacman, ufw, sysctl modules) — installed via `requirements.yml`
- **Local tools:** ansible, openssl, ssh-keygen, python 3.8+
- **Target OS (Tier 2):** Debian/Ubuntu only
- **Target OS (Tier 3):** Arch Linux or Debian/Ubuntu with root access
