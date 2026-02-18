# GEMINI.md - OpenClaw Hardened Ansible Project Context

This file provides instructional context for Gemini CLI interactions within the `openclaw-hardened-ansible` project.

## Project Overview
This project is an automated **Ansible-based deployment** system for a **hardened OpenClaw** instance. It transforms a standard OpenClaw setup into a "Tier 3+" secure environment using a defense-in-depth architecture.

### Key Technologies
- **Ansible:** Orchestrates the system setup and container deployment.
- **Podman (Rootless):** Runs containers as a non-privileged user for enhanced security.
- **LiteLLM:** Acts as a credential broker and model spoofing layer.
- **Squid Proxy:** Filters all outgoing container traffic using a domain allowlist.
- **UFW:** Manages host-level firewall rules.
- **Tailscale:** Provides secure remote access via Tailscale Serve and Tailscale SSH.

### Architecture
1.  **OpenClaw Agent:** The core AI agent service.
2.  **LiteLLM Proxy:** Routes model requests to external providers (Anthropic, OpenAI, Ollama).
3.  **Squid Proxy Sidecar:** All egress traffic from the agent goes through this proxy.
4.  **Host OS Hardening:** Kernel limits (sysctl) and user-level isolation.

## Building and Running

### Deployment
The primary entry point is the `deploy.sh` script, which wraps the Ansible playbook execution.

- **Interactive Deploy:** `./deploy.sh`
- **CLI-driven Deploy:**
  ```bash
  ./deploy.sh -t <TARGET_IP> -p anthropic -m claude-3-5-sonnet-20240620 -k <API_KEY>
  ```

### Maintenance Commands
- **Update Egress Allowlist:** Edit `roles/tier3-setup/templates/allowlist.txt.j2` and run `./update-allowlist.sh`.
- **Check Container Status:** Run `podman ps` on the VPS as the `openclaw` user.
- **OpenClaw Doctor:** `podman exec openclaw-agent openclaw doctor`
- **Manual Device Approval:**
  ```bash
  podman exec openclaw-agent openclaw devices approve <REQUEST_ID>
  ```

## Development Conventions

### Ansible Structure
- **Role-based:** All logic is contained within the `tier3-setup` role.
- **OS Support:** Tasks are split into `arch-system.yml` and `debian-system.yml`.
- **Hardening:** Security-specific tasks are in `security.yml`.
- **Templates:** All configurations (`docker-compose`, `openclaw.json`, `litellm-config`) are Jinja2 templates located in `roles/tier3-setup/templates/`.

### Coding Style & Patterns
- **Rootless Focus:** Always use `become: true` and `become_user: "{{ openclaw_user }}"` for Podman-related tasks.
- **Environment Variables:** Critical secrets are passed via `.env` files generated from Ansible variables.
- **Template Indentation:** For YAML templates (`litellm-config.yaml.j2`), keep Jinja2 control tags (`{% if %}`) at the start of the line to prevent indentation errors in the rendered output.
- **LiteLLM Mapping:** Model IDs are mapped in `litellm-config.yaml.j2` to enable spoofing (e.g., calling a model `claude-sonnet-4-5` even if it's backed by a different provider).

## Important Files
- `playbook.yml`: The main playbook defining variables and roles.
- `deploy.sh`: The interactive deployment wrapper.
- `roles/tier3-setup/templates/openclaw.json.j2`: The primary configuration for the OpenClaw agent.
- `roles/tier3-setup/templates/litellm-config.yaml.j2`: Defines how models are routed and proxied.
- `roles/tier3-setup/templates/docker-compose.yml.j2`: The container stack definition.
- `roles/tier3-setup/tasks/docker-deploy.yml`: The logic for deploying the containerized stack.
