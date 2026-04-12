# Repository Guide

## Overview

This repository contains Ansible automation for OpenClaw deployments.

- `deploy-tier2.sh` and `playbook-tier2.yml` are the **minimal tier 2 bootstrap** path.
- `deploy.sh` and `playbook.yml` remain the **tier 3 container stack** path.

The tier 2 bootstrap is intentionally narrow: it provisions a new VPS, installs OpenClaw, and leaves the instance itself as the source of truth for ongoing agent configuration.

## Tier 2 Scope

Tier 2 should only provision:

- Debian/Ubuntu host prep
- Tailscale installation and auth
- SSH access for the `openclaw` user
- Node.js 22 and OpenClaw installation
- Loopback-bound OpenClaw gateway
- Systemd **system service** running as `openclaw`
- Tailscale Serve exposure
- Initial provider/model config for the main agent
- Optional Telegram, Brave Search, and Gemini embedding config
- Optional seed copy of local legacy scripts into `~/workspace/legacy-scripts`

Tier 2 should not manage:

- extra agents
- OpenClaw cron jobs
- scripts repos
- xurl, reddit, substack, last.fm, obsidian, molt, reminders, or feature tips
- ongoing OpenClaw behavior after bootstrap

## Runtime Model

For tier 2, keep the current service model:

- dedicated OS user: `openclaw`
- systemd **system** service
- gateway bound to `loopback`
- HTTPS exposure via Tailscale Serve

Do not switch tier 2 to:

- running OpenClaw as `root`
- a manual shell-managed process
- a systemd user service as the default

## Working Conventions

- Preserve the 3-play structure in `playbook-tier2.yml`: remote identity check, local key generation, remote bootstrap.
- Keep `deploy-tier2.sh` limited to bootstrap inputs only.
- Prefer idempotent Ansible tasks over shell-heavy post-provisioning flows.
- If adding tier 2 behavior, bias toward removing policy from Ansible and letting the deployed instance manage itself.
- When searching the repo, prefer `rg` and `rg --files`.

## Validation

For tier 2 changes, run at minimum:

```bash
ansible-playbook playbook-tier2.yml --syntax-check
```

When changing deployment inputs, also verify:

- `./deploy-tier2.sh --help`
- success-message output in `playbook-tier2.yml`
- template rendering assumptions for provider config
