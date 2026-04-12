# OpenClaw Ansible Deployments

This repository contains two deployment paths:

- **Tier 2:** minimal direct-host bootstrap for a new OpenClaw VPS
- **Tier 3:** full containerized hardened stack with Podman, LiteLLM, and Squid

## Tier 2 Minimal Bootstrap

Tier 2 provisions a new Debian/Ubuntu VPS with:

- a dedicated `openclaw` user
- SSH key access
- Tailscale and Tailscale Serve
- Node.js 22
- OpenClaw running as a **systemd system service**
- a loopback-bound gateway
- initial config for one main agent
- optional OpenAI Codex OAuth bootstrap via `~/.codex/auth.json`
- optional Telegram, Brave Search, and Gemini embeddings
- optional explicit seed copy of Git-tracked legacy scripts into `~/workspace/legacy-scripts`

Tier 2 does **not** manage ongoing OpenClaw behavior after bootstrap. Agents, cron jobs, skills, and application-level feature changes are expected to be managed on the instance itself.

### Examples

```bash
# Interactive deploy
./deploy-tier2.sh

# Anthropic
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY>

# Ollama
./deploy-tier2.sh -t <IP> -p ollama -m llama3 -u http://localhost:11434

# OpenAI-compatible
./deploy-tier2.sh -t <IP> -p openai_compatible -m <MODEL> -u <BASE_URL> -k <API_KEY>

# OpenAI Codex OAuth (auto-reuses local ~/.codex/auth.json if present)
./deploy-tier2.sh -t <IP> -p openai-codex -m gpt-5.4

# Telegram + Brave + Gemini
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY> \
  --telegram-userid <INTEGER_USER_ID> \
  --telegram-bottoken <BOT_TOKEN> \
  --brave-key <BRAVE_API_KEY> \
  --gemini-key <GEMINI_API_KEY>

# Seed a local legacy scripts snapshot for in-instance migration work
./deploy-tier2.sh -t <IP> -p anthropic -m claude-sonnet-4-5 -k <API_KEY> \
  --seed-legacy-scripts \
  --legacy-scripts-dir ../clamps-tools
```

## Tier 3 Hardened Stack

Tier 3 remains the full containerized deployment:

- rootless Podman
- LiteLLM credential brokering
- Squid egress filtering
- more opinionated hardening and network isolation

Use `./deploy.sh` for that path.

## Maintenance

```bash
ansible-galaxy collection install -r requirements.yml
ansible-playbook playbook-tier2.yml --syntax-check
ansible-playbook playbook.yml --syntax-check
```
