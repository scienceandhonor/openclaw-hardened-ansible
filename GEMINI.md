# GEMINI.md - OpenClaw Hardened Ansible Project Context

This file provides instructional context for Gemini CLI interactions within the `openclaw-hardened-ansible` project.

## Project Overview
This project is an automated **Ansible-based deployment** system for **hardened OpenClaw** instances. It supports two levels of security hardening:

- **Tier 2 (Secure Host):** Direct systemd-based deployment on a hardened Debian/Ubuntu host with Tailscale Serve (HTTPS) and auto-paired CLI.
- **Tier 3+ (Defense-in-Depth):** Containerized deployment using Podman (Rootless), LiteLLM credential brokering, and Squid egress filtering.

### Key Technologies
- **Ansible:** Orchestrates system setup, hardening, and deployment.
- **Tailscale:** Provides secure remote access via Tailscale Serve (HTTPS termination) and Tailscale SSH.
- **Node.js 22:** The required runtime for OpenClaw (CVE-2026-21636 compliance).
- **Podman (Tier 3):** Runs containers as a non-privileged user for enhanced isolation.
- **LiteLLM (Tier 3):** Acts as a credential broker and model spoofing layer.
- **Squid Proxy (Tier 3):** Filters all outgoing container traffic using a domain allowlist.
- **UFW & Fail2Ban:** Manages host-level firewall and brute-force protection.

### Architecture
#### Tier 2 (Direct)
1.  **OpenClaw Gateway:** Runs as a systemd service under the `openclaw` user.
2.  **Tailscale Serve:** Maps `https://<hostname>.ts.net` to local port 18789.
3.  **Auto-Pairing:** Deployment automatically pairs the CLI device to avoid headless UI deadlocks.

#### Tier 3 (Containerized)
1.  **OpenClaw Agent:** Core AI agent service in a rootless container.
2.  **LiteLLM Proxy:** Routes model requests to external providers (Anthropic, OpenAI, Ollama).
3.  **Squid Proxy Sidecar:** All egress traffic from the agent goes through this proxy.
4.  **Host OS Hardening:** Kernel limits (sysctl) and user-level isolation.

## Building and Running

### Deployment
- **Tier 2 (Direct):**
  ```bash
  ./deploy-tier2.sh -t <TARGET_IP> -p ollama -m llama3
  ```
- **Tier 3 (Containerized):**
  ```bash
  ./deploy.sh -t <TARGET_IP> -p anthropic -m claude-3-5-sonnet-20240620 -k <API_KEY>
  ```

### Maintenance Commands
- **Check Status (Tier 2):** `systemctl status openclaw`
- **Check Status (Tier 3):** Run `podman ps` on the VPS as the `openclaw` user.
- **Update Egress Allowlist (Tier 3):** Edit `roles/tier3-setup/templates/allowlist.txt.j2` and run `./update-allowlist.sh`.
- **OpenClaw Doctor:**
  - Tier 2: `openclaw doctor`
  - Tier 3: `podman exec openclaw-agent openclaw doctor`
- **Manual Device Approval:**
  - Tier 2: `openclaw devices approve <REQUEST_ID>`
  - Tier 3: `podman exec openclaw-agent openclaw devices approve <REQUEST_ID>`

## Development Conventions

### Ansible Structure
- **Role-based:** Logic is split between `tier2-setup` (direct host) and `tier3-setup` (containerized).
- **OS Support:**
  - Tier 2: Supports Debian/Ubuntu only.
  - Tier 3: Supports Arch Linux and Debian/Ubuntu.
- **Hardening Logic:** Contained in `security.yml` within each role.
- **Templates:** Configs (`openclaw.json`, `tools.yaml`, etc.) are Jinja2 templates.

### Coding Style & Patterns
- **Gateway Tokens:** MUST be 48-character hex strings (24 bytes). Base64 is rejected by OpenClaw with code 4008.
- **SSH Hardening:** Use `PermitRootLogin prohibit-password` instead of `no` to maintain idempotent Ansible access via keys while blocking passwords.
- **Headless Bootstrap:** Tier 2 uses a Python-based filesystem manipulation to approve the CLI device pairing request in `pending.json` -> `paired.json`.
- **LiteLLM Mapping (Tier 3):** Model IDs are mapped in `litellm-config.yaml.j2` to enable spoofing.

## Important Files
- `playbook-tier2.yml` / `playbook.yml`: Main entry points for Tier 2 and Tier 3.
- `roles/tier2-setup/tasks/install.yml`: Logic for direct host installation and auto-pairing.
- `roles/tier3-setup/tasks/docker-deploy.yml`: Logic for deploying the containerized stack.
- `roles/shared/templates/openclaw.json.j2`: Primary configuration (note: currently duplicated or specialized per tier).
