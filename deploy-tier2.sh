#!/bin/bash
set -e

show_help() {
    echo "Usage: ./deploy-tier2.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target IP       Target IP address"
    echo "  -p, --provider NAME   LLM provider (ollama, anthropic, openai, minimax, openai_compatible)"
    echo "  -m, --model NAME      Model name (e.g. llama3, claude-sonnet-4-5)"
    echo "  -u, --url URL         API base URL (required for ollama and openai_compatible)"
    echo "  -k, --key KEY         API key"
    echo "  --ssh-user USER       Initial SSH user (default: root)"
    echo "  --ssh-key PATH        Path to private key for SSH connection"
    echo "  --ask-pass            Ask for SSH and sudo passwords"
    echo "  --non-interactive     Fail if missing arguments instead of prompting"
    echo "  --telegram-userid ID  Telegram user ID (integer) to allow"
    echo "  --telegram-bottoken T Telegram bot token"
    echo "  --brave-key KEY       Brave Search API key"
    echo "  --gemini-key KEY      Gemini API key for memory embeddings"
    echo "  --legacy-scripts-dir PATH"
    echo "                       Local directory to copy to ~/workspace/legacy-scripts"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Deploys a minimal OpenClaw Tier 2 bootstrap to an Ubuntu/Debian VPS."
    echo ""
}

TARGET_IP=""
SSH_USER=""
LLM_PROVIDER=""
LLM_MODEL=""
LLM_URL=""
LLM_KEY=""
INTERACTIVE=true
ASK_PASS=false
SSH_KEY=""
TELEGRAM_USERID=""
TELEGRAM_BOTTOKEN=""
BRAVE_KEY=""
GEMINI_KEY=""
LEGACY_SCRIPTS_DIR=""

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
        -p|--provider) LLM_PROVIDER="$2"; shift ;;
        -m|--model) LLM_MODEL="$2"; shift ;;
        -u|--url) LLM_URL="$2"; shift ;;
        -k|--key) LLM_KEY="$2"; shift ;;
        --ssh-user) SSH_USER="$2"; shift ;;
        --ssh-key) SSH_KEY="$2"; shift ;;
        --ask-pass) ASK_PASS=true ;;
        --non-interactive) INTERACTIVE=false ;;
        --telegram-userid) TELEGRAM_USERID="$2"; shift ;;
        --telegram-bottoken) TELEGRAM_BOTTOKEN="$2"; shift ;;
        --brave-key) BRAVE_KEY="$2"; shift ;;
        --gemini-key) GEMINI_KEY="$2"; shift ;;
        --legacy-scripts-dir) LEGACY_SCRIPTS_DIR="$2"; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if [ "$INTERACTIVE" = true ]; then
    echo "=================================================="
    echo "   OpenClaw Tier 2 Minimal Bootstrap"
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

    if [ -z "$LLM_PROVIDER" ]; then
        echo ""
        echo "Select LLM provider:"
        echo "  1) Ollama (default)"
        echo "  2) Anthropic"
        echo "  3) OpenAI"
        echo "  4) MiniMax"
        echo "  5) OpenAI-compatible"
        read -p "Choice [1-5]: " provider_choice
        case $provider_choice in
            2) LLM_PROVIDER="anthropic" ;;
            3) LLM_PROVIDER="openai" ;;
            4) LLM_PROVIDER="minimax" ;;
            5) LLM_PROVIDER="openai_compatible" ;;
            *) LLM_PROVIDER="ollama" ;;
        esac
    fi

    if [ -z "$LLM_MODEL" ]; then
        echo ""
        default_model=""
        if [ "$LLM_PROVIDER" == "ollama" ]; then default_model="llama3"; fi
        if [ "$LLM_PROVIDER" == "anthropic" ]; then default_model="claude-sonnet-4-5"; fi
        if [ "$LLM_PROVIDER" == "openai" ]; then default_model="gpt-4o"; fi
        if [ "$LLM_PROVIDER" == "minimax" ]; then default_model="MiniMax-M2.5"; fi
        read -p "Enter model name [$default_model]: " input_model
        LLM_MODEL="${input_model:-$default_model}"
    fi

    if [ -z "$LLM_URL" ]; then
        if [ "$LLM_PROVIDER" == "ollama" ]; then
            echo ""
            read -p "Enter Ollama base URL [http://localhost:11434]: " input_url
            LLM_URL="${input_url:-http://localhost:11434}"
        elif [ "$LLM_PROVIDER" == "openai_compatible" ]; then
            echo ""
            read -p "Enter API base URL: " LLM_URL
        fi
    fi

    if [ -z "$LLM_KEY" ]; then
        if [ "$LLM_PROVIDER" != "ollama" ]; then
            echo ""
            read -s -p "Enter API key: " LLM_KEY
            echo ""
        else
            LLM_KEY="ollama"
        fi
    fi

    if [ -z "$TELEGRAM_USERID" ] && [ -z "$TELEGRAM_BOTTOKEN" ]; then
        echo ""
        read -p "Configure Telegram? [y/N]: " tg_choice
        if [[ "$tg_choice" =~ ^[Yy]$ ]]; then
            read -p "Telegram user ID (integer): " TELEGRAM_USERID
            read -s -p "Telegram bot token: " TELEGRAM_BOTTOKEN
            echo ""
        fi
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
if [ -z "$LLM_PROVIDER" ]; then LLM_PROVIDER="ollama"; fi
if [ -z "$LLM_MODEL" ] && [ "$LLM_PROVIDER" == "ollama" ]; then LLM_MODEL="llama3"; fi
if [ -z "$LLM_URL" ] && [ "$LLM_PROVIDER" == "ollama" ]; then LLM_URL="http://localhost:11434"; fi
if [ -z "$LLM_KEY" ]; then LLM_KEY="sk-placeholder"; fi

if [ -n "$TELEGRAM_BOTTOKEN" ] && [ -z "$TELEGRAM_USERID" ]; then
    echo "Error: --telegram-userid is required when --telegram-bottoken is set."
    exit 1
fi
if [ -n "$TELEGRAM_USERID" ] && [ -z "$TELEGRAM_BOTTOKEN" ]; then
    echo "Error: --telegram-bottoken is required when --telegram-userid is set."
    exit 1
fi

if [ -z "$LEGACY_SCRIPTS_DIR" ] && [ -d "../clamps-tools" ]; then
    LEGACY_SCRIPTS_DIR="../clamps-tools"
fi

if [ -n "$LEGACY_SCRIPTS_DIR" ] && [ ! -d "$LEGACY_SCRIPTS_DIR" ]; then
    echo "Error: legacy scripts directory does not exist: $LEGACY_SCRIPTS_DIR"
    exit 1
fi

echo ""
echo "Deploying Tier 2 Minimal Bootstrap:"
echo "----------------------------------------"
echo "Target:    $TARGET_IP"
echo "User:      $SSH_USER"
if [ -n "$SSH_KEY" ]; then echo "SSH Key:   $SSH_KEY"; fi
echo "OS:        Ubuntu/Debian (auto-detect)"
echo "Provider:  $LLM_PROVIDER / $LLM_MODEL"
if [ -n "$TELEGRAM_USERID" ]; then
    echo "Telegram:  userid=$TELEGRAM_USERID token=***"
else
    echo "Telegram:  not configured"
fi
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
if [ -n "$LEGACY_SCRIPTS_DIR" ]; then
    echo "Legacy:    $LEGACY_SCRIPTS_DIR -> ~/workspace/legacy-scripts"
else
    echo "Legacy:    not configured"
fi
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
    'llm_provider':      sys.argv[1],
    'llm_model':         sys.argv[2],
    'llm_url':           sys.argv[3],
    'llm_key':           sys.argv[4],
    'telegram_userid':   sys.argv[5],
    'telegram_bottoken': sys.argv[6],
    'brave_key':         sys.argv[7],
    'gemini_key':        sys.argv[8],
    'legacy_scripts_dir': sys.argv[9],
}))" "$LLM_PROVIDER" "$LLM_MODEL" "$LLM_URL" "$LLM_KEY" "$TELEGRAM_USERID" "$TELEGRAM_BOTTOKEN" "$BRAVE_KEY" "$GEMINI_KEY" "$LEGACY_SCRIPTS_DIR")

ansible-playbook -i "$TEMP_INVENTORY" playbook-tier2.yml $ANSIBLE_ARGS \
    --extra-vars "$EXTRA_VARS"

rm "$TEMP_INVENTORY"

echo ""
echo "Tier 2 minimal bootstrap finished."
