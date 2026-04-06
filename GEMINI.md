# GEMINI.md - OpenClaw Hardened Ansible Project Context

This file provides instructional context for Gemini CLI interactions within the `openclaw-hardened-ansible` project.

## Project Overview
This project is an automated **Ansible-based deployment** system for **hardened OpenClaw** instances. 

> [!IMPORTANT]
> **Tier 3 (Containerized/Podman) has been discontinued.** The project now focuses exclusively on **Tier 2 (Direct Host)** deployment for maximum performance and reliability on hardened Debian/Ubuntu systems.

### Key Technologies
- **Ansible:** Orchestrates system setup, hardening, and deployment.
- **Tailscale:** Provides secure remote access via Tailscale Serve (HTTPS termination) and Tailscale SSH.
- **Node.js 22:** The required runtime for OpenClaw (CVE-2026-21636 compliance).
- **UFW & Fail2Ban:** Manages host-level firewall and brute-force protection.
- **Cron-based Automation:** Orchestrates periodic fetches (Substack, Reddit, xurl) and agent-led digests.

## Architecture: Tier 2 (Direct)
1.  **OpenClaw Gateway:** Runs as a systemd service under the `openclaw` user.
2.  **Tailscale Serve:** Maps `https://<hostname>.ts.net` to local port 18789.
3.  **Multiple Specialized Agents:** Deployment configures distinct workspaces and personas:
    - **RightClamp (Main):** General purpose agent.
    - **ThePincerMove:** Digest agent for news and social signals. Pinned to `mistral/mistral-medium-2508`.
    - **SirShellspeare:** Roleplay (RP) agent with world-event weaving.
    - **Seneclaw:** Stoic coaching and reflection.

## Building and Running

### Deployment
- **Tier 2 (Direct):**
  ```bash
  ./deploy-tier2.sh -t <TARGET_IP> -p <PROVIDER> -m <MODEL>
  ```
  Supported providers include `anthropic`, `openai_compatible`, `minimax`, `mistral`, and `gemini`.

### Maintenance Commands
- **Check Status:** `systemctl status openclaw`
- **OpenClaw Doctor:** `openclaw doctor`
- **Manual Device Approval:** `openclaw devices approve <REQUEST_ID>`
- **View Logs:** `journalctl -u openclaw -f`

## Development Conventions

### Ansible Structure
- **Tier 2 Focus:** Main logic resides in `roles/tier2-setup`.
- **OS Support:** Debian/Ubuntu only.
- **Hardening Logic:** Contained in `roles/tier2-setup/tasks/security.yml`. Runs **last** to prevent lockout on failure.
- **Templates:** Jinja2 templates for `openclaw.json`, `tools.yaml`, `mcp.json`, and various cron-driven Python scripts.

### Coding Style & Patterns
- **Gateway Tokens:** MUST be 48-character hex strings (24 bytes). Base64 is rejected (Code 4008).
- **Mistral Support:** Requires `apiKey`, `api: "openai-completions"`, and `baseUrl: "https://api.mistral.ai/v1"`. PincerMove uses `mistral/mistral-medium-2508`.
- **Headless Bootstrap:** Tier 2 uses a Python-based filesystem manipulation to approve the CLI device pairing request in `pending.json` -> `paired.json`.
- **Strict Inline Eval:** Global `tools.exec.strictInlineEval: true` is required when allowlisting interpreters (python, node, etc.) to satisfy OpenClaw doctor security checks.
- **Cron Integration:** Heavy use of Python scripts in the playbook to inject jobs into `~/.openclaw/cron/jobs.json`.
- **Gated Announce Pattern:** For jobs with conditional notifications, use `delivery: {mode: none}` in cron and call `openclaw message send` explicitly within the agent prompt only when the condition is met.

### Pipelines & State
- **Substack (Phase 9f):** Hourly system cron fetch → `email-state/undigested.json`. Agent digest at 06:45 and 16:00 UTC.
- **Reddit (Phase 9m):** Hourly system cron fetch → `reddit-state/undigested.json`. Agent digest at 07:30 and 16:30 UTC.
- **xurl (Phase 9k):** Hourly system cron fetch → `timeline-state/undigested.json`. Agent digest at 07:15 and 16:15 UTC. Daily token refresh at 03:30 UTC.
- **RP World Events (Phase 9o):** Hourly signal collection (`gather-world-signals.sh`) → `world-events/pending-signals.json`. RightClamp generates events at 11:00/22:00 UTC → `workspace-rp/pending-events.json`. SirShellspeare nudges at 19:00 UTC.
- **Stoic Coaching (Phase 9q):** Daily theme capture at 06:55 UTC. Seneclaw morning seed (07:20), midday check-in (12:00), evening reflection (19:30), Sunday review (10:00).
- **Obsidian Sync (Phase 9s):** Git-backed R/W vault in `~/obsidian-vault/`. Hourly pull. Post-merge hook triggers scan/summarize.

## Important Files
- `playbook-tier2.yml`: Main entry point for deployment.
- `deploy-tier2.sh`: Wrapper script with argument parsing and extra-vars mapping.
- `roles/tier2-setup/tasks/install.yml`: Core installation logic (Phase 1-9).
- `roles/tier2-setup/templates/openclaw.json.j2`: Primary gateway and provider configuration.
- `roles/tier2-setup/templates/tools.yaml.j2`: Shell and filesystem allowlist configuration.
- `roles/tier2-setup/templates/exec-approvals.json.j2`: Binary execution allowlist.
- `roles/tier2-setup/templates/scripts-config.env.j2`: Rendered with secrets (mode 0600) for clamps-tools scripts.
