#!/bin/bash
set -e

show_help() {
    echo "Usage: ./deploy-tier2.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target IP       Target IP address"
    echo "  --ssh-user USER       Initial SSH user (default: root)"
    echo "  --ssh-key PATH        Path to private key for SSH connection"
    echo "  --openclaw-password P Password to set for the openclaw user (required)"
    echo "  --ask-pass            Ask for SSH and sudo passwords"
    echo "  --non-interactive     Fail if missing arguments instead of prompting"
    echo "  --brave-key KEY       Brave Search API key for OpenClaw web search"
    echo "  --gemini-key KEY      Gemini API key for OpenClaw memory embeddings"
    echo "  --skip-tailscale      Skip Tailscale installation and configuration"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Bootstraps a Debian/Ubuntu VPS for later manual OpenClaw installation."
    echo ""
}

TARGET_IP=""
SSH_USER=""
INTERACTIVE=true
ASK_PASS=false
SSH_KEY=""
OPENCLAW_PASSWORD=""
BRAVE_KEY=""
GEMINI_KEY=""
SKIP_TAILSCALE=false

_ARGS=()
for _arg in "$@"; do
    if [[ "$_arg" == --*=* ]]; then
        _ARGS+=("${_arg%%=*}" "${_arg#*=}")
    else
        _ARGS+=("$_arg")
    fi
done
set -- "${_ARGS[@]+"${_ARGS[@]}"}"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -t|--target) TARGET_IP="$2"; shift ;;
        --ssh-user) SSH_USER="$2"; shift ;;
        --ssh-key) SSH_KEY="$2"; shift ;;
        --openclaw-password) OPENCLAW_PASSWORD="$2"; shift ;;
        --ask-pass) ASK_PASS=true ;;
        --non-interactive) INTERACTIVE=false ;;
        --brave-key) BRAVE_KEY="$2"; shift ;;
        --gemini-key) GEMINI_KEY="$2"; shift ;;
        --skip-tailscale) SKIP_TAILSCALE=true ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if [ "$INTERACTIVE" = true ]; then
    echo "=================================================="
    echo "   OpenClaw VPS Bare-Minimum Bootstrap"
    echo "=================================================="
    echo ""

    if [ -z "$TARGET_IP" ]; then
        read -p "Enter target host IP: " TARGET_IP
    fi

    if [ -z "$SSH_USER" ]; then
        read -p "Initial SSH user [root]: " input_user
        SSH_USER="${input_user:-root}"
    fi

    if [ -z "$SSH_KEY" ] && [ "$ASK_PASS" = false ]; then
        echo ""
        read -p "SSH private key path (leave empty for default/ssh-agent): " input_key
        SSH_KEY="${input_key}"
    fi

    if [ -z "$OPENCLAW_PASSWORD" ]; then
        echo ""
        read -s -p "Enter password for openclaw user: " OPENCLAW_PASSWORD
        echo ""
    fi

    if [ -z "$BRAVE_KEY" ]; then
        echo ""
        read -p "Brave Search API key (leave empty to skip): " input_brave
        BRAVE_KEY="${input_brave}"
    fi

    if [ -z "$GEMINI_KEY" ]; then
        echo ""
        read -p "Gemini embedding key (leave empty to skip): " input_gemini
        GEMINI_KEY="${input_gemini}"
    fi
fi

if [ -z "$TARGET_IP" ]; then
    echo "Error: target IP is required."
    exit 1
fi

if [ -z "$SSH_USER" ]; then SSH_USER="root"; fi

echo ""
echo "Deploying Bare-Minimum VPS Bootstrap:"
echo "----------------------------------------"
echo "Target:    $TARGET_IP"
echo "User:      $SSH_USER"
if [ -n "$SSH_KEY" ]; then echo "SSH Key:   $SSH_KEY"; fi
if [ -n "$OPENCLAW_PASSWORD" ]; then echo "Password:  openclaw=***"; fi
echo "OS:        Ubuntu/Debian (auto-detect)"
if [ -n "$BRAVE_KEY" ]; then
    echo "Brave:     enabled (key=***)"
else
    echo "Brave:     not configured"
fi
if [ -n "$GEMINI_KEY" ]; then
    echo "Gemini:    enabled (key=***)"
else
    echo "Gemini:    not configured"
fi
if [ "$SKIP_TAILSCALE" = true ]; then
    echo "Tailscale: skipped"
else
    echo "Tailscale: enabled"
fi
echo "Goal:      login-ready host bootstrap only"
echo "----------------------------------------"

TEMP_INVENTORY=$(mktemp)
echo "[openclaw_hosts]" > "$TEMP_INVENTORY"
echo "$TARGET_IP ansible_user=$SSH_USER" >> "$TEMP_INVENTORY"

check_dep() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed locally. Please install it first."
        exit 1
    fi
}

check_dep ssh-keygen
check_dep ansible
check_dep ansible-playbook

if [ ! -f "eff_large_wordlist.txt" ]; then
    echo "Error: eff_large_wordlist.txt not found in current directory."
    exit 1
fi

echo "Installing Ansible collections..."
ansible-galaxy collection install -r requirements.yml > /dev/null

ANSIBLE_ARGS=""
if [ "$ASK_PASS" = true ]; then
    ANSIBLE_ARGS="-k -K"
fi
if [ -n "$SSH_KEY" ]; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS --private-key=$SSH_KEY"
fi

EXTRA_VARS=$(python3 -c "
import json, sys
print(json.dumps({
    'openclaw_password': sys.argv[1],
    'brave_key':         sys.argv[2],
    'gemini_key':        sys.argv[3],
    'install_tailscale': sys.argv[4] != 'true',
    'install_deploy_key': sys.argv[5] == '',
}))" "$OPENCLAW_PASSWORD" "$BRAVE_KEY" "$GEMINI_KEY" "$SKIP_TAILSCALE" "$SSH_KEY")

ansible-playbook -i "$TEMP_INVENTORY" playbook-tier2.yml $ANSIBLE_ARGS \
    --extra-vars "$EXTRA_VARS"

rm "$TEMP_INVENTORY"

echo ""
echo "Bare-minimum VPS bootstrap finished."
