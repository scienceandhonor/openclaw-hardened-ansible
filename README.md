# OpenClaw Ansible Deployments

This repository contains two deployment paths:

- **Tier 2:** bare-minimum direct-host bootstrap for a new OpenClaw VPS
- **Tier 3:** full containerized hardened stack with Podman, LiteLLM, and Squid

## Tier 2 Bare-Minimum Bootstrap

Tier 2 provisions a new Debian/Ubuntu VPS with:

- a dedicated `openclaw` user
- a required password set for that `openclaw` user
- SSH key access
- Tailscale with SSH enabled
- Node.js 22
- Homebrew for the `openclaw` user
- a login-ready shell environment for manual OpenClaw installation

Tier 2 does **not** install or configure OpenClaw itself. After bootstrap, you log in as `openclaw` over Tailscale SSH and install or configure OpenClaw manually on the VPS.

### Examples

```bash
# Interactive deploy
./deploy-tier2.sh

# Non-interactive with explicit SSH user and key
./deploy-tier2.sh -t <IP> --ssh-user root --ssh-key ~/.ssh/id_ed25519 \
  --openclaw-password <PASSWORD> --non-interactive
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
