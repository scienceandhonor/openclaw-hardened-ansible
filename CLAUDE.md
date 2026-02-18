# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Ansible deployment for hardened OpenClaw AI agents (Tier 3+ security). Deploys rootless Podman containers with egress filtering, credential brokering, and host-level hardening to Arch Linux or Debian/Ubuntu targets.

## Commands

### Deployment
```bash
# Interactive deploy (prompts for IP, provider, API keys)
./deploy.sh

# CLI-driven deploy
./deploy.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY>

# AWS/cloud with SSH key
./deploy.sh --target <IP> --ssh-user ubuntu --ssh-key ~/key.pem --provider ollama --model "deepseek-r1:8b" --url "http://10.100.1.25:11434"
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
```

## Architecture

### Playbook Structure
`playbook.yml` has 3 plays: (1) check for existing installation identity on remote, (2) local key/hostname generation using EFF wordlist, (3) call `tier3-setup` role for full deployment.

All logic lives in a single role: `roles/tier3-setup/`.

### Task Flow (roles/tier3-setup/tasks/)
- `main.yml` — OS detection (Arch vs Debian/Ubuntu), sysctl kernel limits, includes other task files
- `arch-system.yml` / `debian-system.yml` — OS-specific package install, user creation, rootless Podman setup, Tailscale auth
- `security.yml` — UFW firewall rules, Fail2Ban, SSH hardening
- `docker-deploy.yml` — Template rendering, secret generation/persistence, Podman image build, container startup, health checks, device pairing, Tailscale Serve config

### Container Stack (deployed via Podman Compose)
- **OpenClaw Agent** — Node.js 22-Alpine AI agent runtime, exposed on port 18789 (HTTPS)
- **LiteLLM** — Credential broker + model spoofing proxy on port 4000 (internal only)
- **Squid** — Domain allowlist egress proxy on port 3128 (internal only)

### Network Isolation
Two Podman networks: `openclaw-internal` (agent ↔ LiteLLM ↔ Squid) and `openclaw-external` (Squid-only outbound). Only port 18789 is host-bound. All container egress routes through Squid's domain allowlist.

### Secret Management
Tokens (gateway token, LiteLLM master key) are generated on first deploy and persisted in the remote `.env` file. Subsequent runs detect and reuse existing secrets rather than regenerating.

## Development Conventions

- **Rootless Podman:** Always use `become: true` with `become_user: "{{ openclaw_user }}"` for Podman tasks.
- **Template indentation:** For YAML templates (especially `litellm-config.yaml.j2`), keep Jinja2 control tags (`{% if %}`) at column 0 to prevent indentation errors in rendered output.
- **LiteLLM model mapping:** Model IDs in `litellm-config.yaml.j2` enable spoofing — a model named `claude-sonnet-4-5` can be backed by any provider.
- **Commit style:** Use conventional commits with scope, e.g. `fix(litellm):`, `feat(network):`, `security(litellm):`.

## Key Files

- `deploy.sh` — Interactive/CLI deployment wrapper; validates deps, generates inventory, runs playbook
- `playbook.yml` — Main playbook defining variables and role inclusion
- `roles/tier3-setup/templates/docker-compose.yml.j2` — Container stack definition
- `roles/tier3-setup/templates/openclaw.json.j2` — Primary OpenClaw agent configuration
- `roles/tier3-setup/templates/litellm-config.yaml.j2` — LLM provider routing and model mapping
- `roles/tier3-setup/templates/allowlist.txt.j2` — Egress domain whitelist (edit this to add allowed domains)
- `roles/tier3-setup/tasks/docker-deploy.yml` — Container deployment logic (largest task file)

## Dependencies

- **Ansible collection:** `community.general` (for pacman, ufw, sysctl modules) — installed via `requirements.yml`
- **Local tools:** ansible, openssl, ssh-keygen, python 3.8+
- **Target OS:** Arch Linux or Debian/Ubuntu with root access
