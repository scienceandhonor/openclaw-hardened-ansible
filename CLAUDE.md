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
```

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
- `install.yml` — Node.js 22 via NodeSource (with version guard), openclaw npm install, directory structure, gateway token generation, systemd service, doctor fix, health check, **CLI device pairing bootstrap**, Tailscale Serve HTTPS, weekly monitoring cron
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
Tier 2: Gateway token generated with `openssl rand -hex 24` (must be 48-char hex — openclaw rejects base64 tokens at connection time). Persisted to `~/.openclaw/gateway.token`. Re-runs reuse the existing token. Provider API key written directly to `openclaw.json` by the template.

## Development Conventions

- **Rootless Podman (Tier 3):** Always use `become: true` with `become_user: "{{ openclaw_user }}"` for Podman tasks.
- **Template indentation:** For YAML templates (especially `litellm-config.yaml.j2`), keep Jinja2 control tags (`{% if %}`) at column 0 to prevent indentation errors in rendered output.
- **LiteLLM model mapping (Tier 3):** Model IDs in `litellm-config.yaml.j2` enable spoofing — a model named `claude-sonnet-4-5` can be backed by any provider.
- **Tier 2 provider config:** Provider/model/URL/key are injected directly into `openclaw.json.j2` via Jinja2 conditionals — no LiteLLM intermediary.
- **Commit style:** Use conventional commits with scope, e.g. `fix(litellm):`, `feat(tier2):`, `security(ssh):`.

## openclaw.json Schema Notes (Tier 2)

Hard-won constraints from live deployment — openclaw doctor/validator enforces these:

- **`gateway.bind`** — Valid values are keywords (`"loopback"`, `"lan"`, etc.), not IP strings. `"lo"` and `"127.0.0.1"` are rejected with schema errors. Use `"loopback"` for tier 2.
- **`gateway.auth.token`** — Must be a 48-char hex string (`openssl rand -hex 24`). Base64 tokens are silently rejected at WebSocket connection time with code 4008.
- **`gateway.remote.token` / `gateway.remote.url`** — Client-side config for the CLI to connect to a remote gateway. Set these to allow CLI commands to authenticate without device pairing prompts.
- **`models.providers.<provider>.baseUrl`** — Required field for anthropic and openai providers. Omitting it causes schema validation failure on startup.
- **`models.providers.<provider>.models`** — Required array for anthropic and openai providers. Must include at least the configured model.
- **`channels.discord.dmPolicy`** — Correct field name. `channels.discord.dm.policy` is the old format; openclaw doctor migrates it automatically but the template should use the new form to avoid constant migration noise.
- **Semantic memory** — openclaw auto-detects embedding providers (OpenAI, Gemini, Voyage, or local GGUF model) and falls back to BM25-only if none are available. Do not explicitly disable it.

## openclaw Device Pairing (Tier 2 Headless Bootstrap)

openclaw has two separate auth layers that are easy to conflate:

1. **Gateway auth token** (`gateway.auth.token`) — Authenticates the browser dashboard WebSocket (controlUI). Set `gateway.remote.token` client-side for the CLI to use this token.
2. **Device pairing** — Separate per-device asymmetric key challenge. Required for CLI connections regardless of gateway token. `dangerouslyDisableDeviceAuth` only bypasses this for the controlUI, not the CLI.

**`OPENCLAW_GATEWAY_TOKEN` env var does not bypass device pairing for the CLI.** It is only for the agent API, not the control plane WebSocket.

**Headless bootstrap flow** (automated in `install.yml` Phase 7b):
1. Run any CLI command — it fails but generates `~/.openclaw/identity/device.json` (Ed25519 key pair) and writes a pending entry to `~/.openclaw/devices/pending.json`
2. Move the CLI's pending entry into `~/.openclaw/devices/paired.json` (keyed by `deviceId`, drop `requestId`, add `pairedAt`)
3. Restart the gateway — it reads `paired.json` on startup and trusts the CLI's public key
4. CLI connects using private key challenge from `identity/device.json`

Browser pairing is done manually post-deploy: open the dashboard URL from `openclaw dashboard --no-open` via SSH tunnel, the browser submits a pending request, approve with `openclaw nodes approve <requestId>` from the now-working CLI.

## Key Files

### Tier 2
- `deploy-tier2.sh` — Interactive/CLI deployment wrapper for tier 2
- `playbook-tier2.yml` — Tier 2 playbook (identity check, key gen, tier2-setup role)
- `roles/tier2-setup/tasks/install.yml` — Main install logic (Node.js, openclaw, systemd, Tailscale Serve)
- `roles/tier2-setup/templates/openclaw.json.j2` — Agent config with direct provider routing
- `roles/tier2-setup/templates/tools.yaml.j2` — Shell allowlist and filesystem permissions
- `roles/tier2-setup/templates/mcp.json.j2` — MCP server config (memory server only)
- `roles/tier2-setup/templates/exec-approvals.json.j2` — Approved binary paths
- `roles/tier2-setup/templates/monitor-openclaw.sh.j2` — Weekly security audit script

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
