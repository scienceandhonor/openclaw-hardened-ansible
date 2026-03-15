#!/bin/bash
set -e

# Help Function
show_help() {
    echo "Usage: ./deploy-tier2.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target IP       Target IP address"
    echo "  -p, --provider NAME   LLM Provider (ollama, anthropic, openai, minimax, openai_compatible)"
    echo "  -m, --model NAME      Model Name (e.g., llama3, claude-sonnet-4-5)"
    echo "  -u, --url URL         API Base URL (required for ollama and openai_compatible)"
    echo "  -k, --key KEY         API Key"
    echo "  --ssh-user USER       Initial SSH User (Default: root)"
    echo "  --ssh-key PATH        Path to private key for SSH connection"
    echo "  --ask-pass            Ask for SSH and Sudo passwords"
    echo "  --non-interactive     Fail if missing arguments instead of prompting"
    echo "  --telegram-userid ID  Telegram user ID (integer) to allow"
    echo "  --telegram-bottoken T Telegram bot token"
    echo "  --brave-key KEY       Brave Search API key (enables web search tool)"
    echo "  --lastfm-key KEY      Last.fm API key (enables hourly artist sync)"
    echo "  --lastfm-user USER    Last.fm username to track"
    echo "  --scripts-repo SLUG   GitHub repo slug for operational scripts (e.g. user/clamps-tools)"
    echo "  --email-imap-host H   IMAP server hostname (e.g. imap.gmail.com) — enables Substack digest"
    echo "  --email-imap-user U   IMAP login address"
    echo "  --email-imap-password P  IMAP app password"
    echo "  --email-folder F      IMAP folder/label to poll (default: INBOX)"
    echo "  --rp-telegram-bottoken T  Telegram bot token for SirShellspeare RP bot (MiniMax only)
  --enable-reddit       Enable Reddit digest (uses public JSON API — no credentials needed)"
    echo "  --gemini-key KEY      Gemini API key (enables semantic memory search via embeddings)
  --openrouter-key KEY  OpenRouter API key (enables OpenRouter models e.g. for PincerMove agent)"
    echo "  --molt-api-key KEY    Church of Molt API key (deploys crustafarianism skill — requires --scripts-repo)
  --molt-agent-name N   Agent name recorded in Molt credentials (default: Agent)
  --moltbook-api-key KEY  Moltbook API key for Sociaclamps (deploys Sociaclamps subagent — requires --scripts-repo)
  --moltbook-agent-name N Agent name on Moltbook (default: Sociaclamps)
  --anthropic-api-key KEY Anthropic API key for Sociaclamps's Claude Sonnet 4.6 model
  --moltbook-telegram-bottoken T  Telegram bot token for Sociaclamps's own bot
  --vault-file FILE     Ansible Vault-encrypted vars file (e.g. vault-xurl.yml)"
    echo "  --vault-password PASS Vault password (for non-interactive deploys)"
    echo "  --reset-xurl-token    Overwrite ~/.xurl on VPS with vault copy (use when token is broken)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Deploys OpenClaw Tier 2 (direct host, no containers) to an Ubuntu/Debian VPS."
    echo ""
}

# Defaults
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
LASTFM_KEY=""
LASTFM_USERNAME=""
SCRIPTS_REPO=""
EMAIL_IMAP_HOST=""
EMAIL_IMAP_USER=""
EMAIL_IMAP_PASSWORD=""
EMAIL_FOLDER=""
RP_TELEGRAM_BOTTOKEN=""
REDDIT_ENABLED=false
VAULT_FILE=""
VAULT_PASSWORD=""
RESET_XURL_TOKEN=false
GEMINI_KEY=""
OPENROUTER_KEY=""
MOLT_API_KEY=""
MOLT_AGENT_NAME=""
MOLTBOOK_API_KEY=""
MOLTBOOK_AGENT_NAME=""
ANTHROPIC_API_KEY=""
MOLTBOOK_TELEGRAM_BOTTOKEN=""

# Normalize --flag=value into --flag value so both forms work
_ARGS=()
for _arg in "$@"; do
    if [[ "$_arg" == --*=* ]]; then
        _ARGS+=("${_arg%%=*}" "${_arg#*=}")
    else
        _ARGS+=("$_arg")
    fi
done
set -- "${_ARGS[@]+"${_ARGS[@]}"}"

# Parse Arguments
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
        --lastfm-key) LASTFM_KEY="$2"; shift ;;
        --lastfm-user) LASTFM_USERNAME="$2"; shift ;;
        --scripts-repo) SCRIPTS_REPO="$2"; shift ;;
        --email-imap-host) EMAIL_IMAP_HOST="$2"; shift ;;
        --email-imap-user) EMAIL_IMAP_USER="$2"; shift ;;
        --email-imap-password) EMAIL_IMAP_PASSWORD="$2"; shift ;;
        --email-folder) EMAIL_FOLDER="$2"; shift ;;
        --rp-telegram-bottoken) RP_TELEGRAM_BOTTOKEN="$2"; shift ;;
        --enable-reddit) REDDIT_ENABLED=true ;;
        --reset-xurl-token) RESET_XURL_TOKEN=true ;;
        --gemini-key) GEMINI_KEY="$2"; shift ;;
        --openrouter-key) OPENROUTER_KEY="$2"; shift ;;
        --molt-api-key) MOLT_API_KEY="$2"; shift ;;
        --molt-agent-name) MOLT_AGENT_NAME="$2"; shift ;;
        --moltbook-api-key) MOLTBOOK_API_KEY="$2"; shift ;;
        --moltbook-agent-name) MOLTBOOK_AGENT_NAME="$2"; shift ;;
        --anthropic-api-key) ANTHROPIC_API_KEY="$2"; shift ;;
        --moltbook-telegram-bottoken) MOLTBOOK_TELEGRAM_BOTTOKEN="$2"; shift ;;
        --vault-file) VAULT_FILE="$2"; shift ;;
        --vault-password) VAULT_PASSWORD="$2"; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# --- Interactive Prompts ---

if [ "$INTERACTIVE" = true ]; then
    echo "=================================================="
    echo "   🛡️  OpenClaw Tier 2 Deployment"
    echo "   (Direct host — no containers)"
    echo "=================================================="
    echo ""

    if [ -z "$TARGET_IP" ]; then
        read -p "Enter Target Host IP: " TARGET_IP
    fi

    if [ -z "$SSH_USER" ]; then
        read -p "Initial SSH User [root]: " input_user
        SSH_USER="${input_user:-root}"
    fi

    if [ -z "$SSH_KEY" ] && [ "$ASK_PASS" = false ]; then
        echo ""
        echo "Enter path to SSH Private Key (leave empty for default/ssh-agent):"
        read -p "Key Path: " input_key
        SSH_KEY="${input_key}"
    fi

    if [ -z "$LLM_PROVIDER" ]; then
        echo ""
        echo "Select LLM Provider:"
        echo "  1) Ollama (Default)"
        echo "  2) Anthropic"
        echo "  3) OpenAI"
        echo "  4) MiniMax"
        echo "  5) OpenAI-compatible (custom base URL)"
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

        read -p "Enter Model Name [$default_model]: " input_model
        LLM_MODEL="${input_model:-$default_model}"
    fi

    if [ -z "$LLM_URL" ]; then
        if [ "$LLM_PROVIDER" == "ollama" ]; then
            echo ""
            read -p "Enter Ollama Base URL [http://localhost:11434]: " input_url
            LLM_URL="${input_url:-http://localhost:11434}"
        elif [ "$LLM_PROVIDER" == "openai_compatible" ]; then
            echo ""
            read -p "Enter API Base URL: " LLM_URL
        fi
        # minimax: base URL is hardcoded in the template
    fi

    if [ -z "$LLM_KEY" ]; then
        if [ "$LLM_PROVIDER" != "ollama" ]; then
            echo ""
            read -s -p "Enter API Key: " LLM_KEY
            echo ""
        else
            LLM_KEY="ollama"
        fi
    fi

    if [ -z "$TELEGRAM_USERID" ] && [ -z "$TELEGRAM_BOTTOKEN" ]; then
        echo ""
        read -p "Configure Telegram? [y/N]: " tg_choice
        if [[ "$tg_choice" =~ ^[Yy]$ ]]; then
            read -p "Telegram User ID (integer): " TELEGRAM_USERID
            read -s -p "Telegram Bot Token: " TELEGRAM_BOTTOKEN
            echo ""
        fi
    fi

    if [ -z "$BRAVE_KEY" ]; then
        echo ""
        read -p "Enable Brave Search? Enter API key or leave empty to skip: " input_brave
        BRAVE_KEY="${input_brave}"
    fi

    if [ -z "$LASTFM_KEY" ] && [ -z "$LASTFM_USERNAME" ]; then
        echo ""
        read -p "Enable Last.fm artist sync? Enter Last.fm username or leave empty to skip: " input_lastfm_user
        if [ -n "$input_lastfm_user" ]; then
            LASTFM_USERNAME="$input_lastfm_user"
            read -s -p "Last.fm API key: " LASTFM_KEY
            echo ""
        fi
    fi

    if [ -z "$SCRIPTS_REPO" ]; then
        echo ""
        read -p "GitHub scripts repo slug (e.g. user/clamps-tools, leave empty to skip): " SCRIPTS_REPO
    fi

    if [ -z "$EMAIL_IMAP_HOST" ] && [ -z "$EMAIL_IMAP_USER" ]; then
        echo ""
        read -p "Enable Substack email digest? Enter IMAP host (e.g. imap.gmail.com) or leave empty to skip: " EMAIL_IMAP_HOST
        if [ -n "$EMAIL_IMAP_HOST" ]; then
            read -p "IMAP username (your email address): " EMAIL_IMAP_USER
            read -s -p "IMAP app password: " EMAIL_IMAP_PASSWORD
            echo ""
            read -p "IMAP folder to poll [INBOX]: " input_folder
            EMAIL_FOLDER="${input_folder:-INBOX}"
        fi
    fi

fi

# --- Validation ---

if [ -z "$TARGET_IP" ]; then
    echo "Error: Target IP is required."
    exit 1
fi

if [ -z "$SSH_USER" ]; then SSH_USER="root"; fi
if [ -z "$LLM_PROVIDER" ]; then LLM_PROVIDER="ollama"; fi
if [ -z "$LLM_MODEL" ] && [ "$LLM_PROVIDER" == "ollama" ]; then LLM_MODEL="llama3"; fi
if [ -z "$LLM_URL" ] && [ "$LLM_PROVIDER" == "ollama" ]; then LLM_URL="http://localhost:11434"; fi
if [ -z "$LLM_KEY" ]; then LLM_KEY="sk-placeholder"; fi

# Require both Telegram params or neither
if [ -n "$LASTFM_KEY" ] && [ -z "$LASTFM_USERNAME" ]; then
    echo "Error: --lastfm-user is required when --lastfm-key is set."
    exit 1
fi
if [ -n "$LASTFM_USERNAME" ] && [ -z "$LASTFM_KEY" ]; then
    echo "Error: --lastfm-key is required when --lastfm-user is set."
    exit 1
fi

if [ -n "$TELEGRAM_BOTTOKEN" ] && [ -z "$TELEGRAM_USERID" ]; then
    echo "Error: --telegram-userid is required when --telegram-bottoken is set."
    exit 1
fi
if [ -n "$TELEGRAM_USERID" ] && [ -z "$TELEGRAM_BOTTOKEN" ]; then
    echo "Error: --telegram-bottoken is required when --telegram-userid is set."
    exit 1
fi

# Email: all three required fields must be provided together
EMAIL_FIELDS_SET=0
[ -n "$EMAIL_IMAP_HOST" ] && EMAIL_FIELDS_SET=$((EMAIL_FIELDS_SET + 1))
[ -n "$EMAIL_IMAP_USER" ] && EMAIL_FIELDS_SET=$((EMAIL_FIELDS_SET + 1))
[ -n "$EMAIL_IMAP_PASSWORD" ] && EMAIL_FIELDS_SET=$((EMAIL_FIELDS_SET + 1))
if [ "$EMAIL_FIELDS_SET" -gt 0 ] && [ "$EMAIL_FIELDS_SET" -lt 3 ]; then
    echo "Error: --email-imap-host, --email-imap-user, and --email-imap-password must all be provided together."
    exit 1
fi
# Email digest requires the scripts repo: the IMAP poller and prompt live in clamps-tools
if [ "$EMAIL_FIELDS_SET" -eq 3 ] && [ -z "$SCRIPTS_REPO" ]; then
    echo "Error: --scripts-repo is required when email digest is configured."
    echo "       The IMAP poller and prompt (check-substack-email.py, substack-prompt.txt)"
    echo "       are deployed via clamps-tools, not directly by Ansible."
    exit 1
fi
if [ -z "$EMAIL_FOLDER" ]; then EMAIL_FOLDER="INBOX"; fi

# --- Execution ---

echo ""
echo "Deploying Tier 2 Configuration:"
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
if [ -n "$LASTFM_USERNAME" ]; then
    echo "Last.fm:   user=$LASTFM_USERNAME key=***"
else
    echo "Last.fm:   not configured"
fi
if [ -n "$SCRIPTS_REPO" ]; then
    echo "Scripts:   $SCRIPTS_REPO (r/o deploy key)"
else
    echo "Scripts:   not configured"
fi
if [ -n "$EMAIL_IMAP_HOST" ]; then
    echo "Email:     $EMAIL_IMAP_USER @ $EMAIL_IMAP_HOST (folder: $EMAIL_FOLDER)"
else
    echo "Email:     not configured"
fi
if [ -n "$RP_TELEGRAM_BOTTOKEN" ]; then
    echo "RP bot:    SirShellspeare token=***"
else
    echo "RP bot:    not configured"
fi
if [ "$REDDIT_ENABLED" = true ]; then
    echo "Reddit:    enabled (public JSON API)"
else
    echo "Reddit:    not configured"
fi
if [ -n "$GEMINI_KEY" ]; then
    echo "Gemini:    embedding key=***"
else
    echo "Gemini:    not configured"
fi
if [ -n "$OPENROUTER_KEY" ]; then
    echo "OpenRouter: key=***"
else
    echo "OpenRouter: not configured"
fi
if [ -n "$MOLTBOOK_API_KEY" ]; then
    echo "Moltbook:  Sociaclamps agent (key=***)"
else
    echo "Moltbook:  not configured"
fi
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "Anthropic: Sociaclamps model key=***"
else
    echo "Anthropic: not configured"
fi
if [ -n "$MOLTBOOK_TELEGRAM_BOTTOKEN" ]; then
    echo "Molt bot:  Sociaclamps token=***"
else
    echo "Molt bot:  not configured"
fi
if [ -n "$VAULT_FILE" ]; then
    echo "Vault:     $VAULT_FILE"
fi
if [ "$RESET_XURL_TOKEN" = true ]; then
    echo "xurl:      token will be OVERWRITTEN from vault"
fi
echo "----------------------------------------"

# Create temporary inventory
TEMP_INVENTORY=$(mktemp)
echo "[openclaw_hosts]" > "$TEMP_INVENTORY"
echo "$TARGET_IP ansible_user=$SSH_USER" >> "$TEMP_INVENTORY"

# Check Local Dependencies
check_dep() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed locally. Please install it first."
        exit 1
    fi
}

check_dep ssh-keygen
check_dep ansible
check_dep ansible-playbook

# Check Wordlist
if [ ! -f "eff_large_wordlist.txt" ]; then
    echo "Error: eff_large_wordlist.txt not found in current directory."
    exit 1
fi

# Install Ansible Requirements
echo "📦 Installing Ansible collections..."
ansible-galaxy collection install -r requirements.yml > /dev/null

# Build ansible-playbook arguments
ANSIBLE_ARGS=""
if [ "$ASK_PASS" = true ]; then
    ANSIBLE_ARGS="-k -K"
fi
if [ -n "$SSH_KEY" ]; then
    ANSIBLE_ARGS="$ANSIBLE_ARGS --private-key=$SSH_KEY"
fi
TEMP_VAULT_PASS=""
if [ -n "$VAULT_FILE" ]; then
    if [ -n "$VAULT_PASSWORD" ]; then
        TEMP_VAULT_PASS=$(mktemp)
        printf '%s' "$VAULT_PASSWORD" > "$TEMP_VAULT_PASS"
        ANSIBLE_ARGS="$ANSIBLE_ARGS --extra-vars @${VAULT_FILE} --vault-password-file=${TEMP_VAULT_PASS}"
    else
        ANSIBLE_ARGS="$ANSIBLE_ARGS --extra-vars @${VAULT_FILE} --ask-vault-pass"
    fi
fi

# Build extra-vars as JSON so special characters (e.g. colons in bot tokens) are never misinterpreted
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
    'lastfm_api_key':    sys.argv[8],
    'lastfm_username':   sys.argv[9],
    'scripts_repo_slug':   sys.argv[10],
    'email_imap_host':     sys.argv[11],
    'email_imap_user':     sys.argv[12],
    'email_imap_password': sys.argv[13],
    'email_imap_folder':   sys.argv[14],
    'rp_telegram_bottoken': sys.argv[15],
    'reddit_enabled':        sys.argv[16] == 'true',
    'xurl_force_token':      sys.argv[17] == 'true',
    'gemini_key':            sys.argv[18],
    'openrouter_key':        sys.argv[19],
    'molt_api_key':          sys.argv[20],
    'molt_agent_name':       sys.argv[21],
    'moltbook_api_key':      sys.argv[22],
    'moltbook_agent_name':   sys.argv[23],
    'anthropic_api_key':     sys.argv[24],
    'moltbook_telegram_bottoken': sys.argv[25],
}))" "$LLM_PROVIDER" "$LLM_MODEL" "$LLM_URL" "$LLM_KEY" "$TELEGRAM_USERID" "$TELEGRAM_BOTTOKEN" "$BRAVE_KEY" "$LASTFM_KEY" "$LASTFM_USERNAME" "$SCRIPTS_REPO" "$EMAIL_IMAP_HOST" "$EMAIL_IMAP_USER" "$EMAIL_IMAP_PASSWORD" "$EMAIL_FOLDER" "$RP_TELEGRAM_BOTTOKEN" "$REDDIT_ENABLED" "$RESET_XURL_TOKEN" "$GEMINI_KEY" "$OPENROUTER_KEY" "$MOLT_API_KEY" "$MOLT_AGENT_NAME" "$MOLTBOOK_API_KEY" "$MOLTBOOK_AGENT_NAME" "$ANTHROPIC_API_KEY" "$MOLTBOOK_TELEGRAM_BOTTOKEN")

# Run Playbook
ansible-playbook -i "$TEMP_INVENTORY" playbook-tier2.yml $ANSIBLE_ARGS \
    --extra-vars "$EXTRA_VARS"

# Cleanup
rm "$TEMP_INVENTORY"
[ -n "$TEMP_VAULT_PASS" ] && rm -f "$TEMP_VAULT_PASS"

echo ""
echo "✅ Tier 2 deployment finished."
