# Plan: Obsidian Vault Sync Strategy (Git-backed, Read+Write)

## Context

The user wants the RightClamp agent to access their Obsidian vault on the VPS for full read/write operations — searching notes, creating new ones, and moving/renaming with wikilink integrity. The vault is a git repo; the VPS gets a clone with a deploy key (mirrors the existing `--scripts-repo` pattern). A SKILL.md exposes the capability to the agent. An hourly cron keeps the vault in sync bidirectionally.

---

## Setup Order (Critical — Dependencies Exist)

1. **Install `obsidian-cli`** via npm global before vault setup (agent needs the binary to interact with vault)
2. **Generate deploy key** + pause for user to add to GitHub (identical to scripts-repo pattern)
3. **Clone vault** to `~/obsidian-vault/`
4. **Register vault** with obsidian-cli by writing `~/.config/obsidian/obsidian.json` (headless VPS has no Obsidian desktop — must create this file manually)
5. **Set default vault** via `obsidian-cli set-default`
6. **Deploy SKILL.md** (after dir creation + obsidian-cli is available)
7. **System cron** — hourly pull + auto-commit-push (safety net for agent writes)
8. **Update tools.yaml + exec-approvals** — grant vault path and git/obsidian-cli binaries

---

## Files to Create / Modify

### New files
- `roles/tier2-setup/files/skills/obsidian/SKILL.md` — Linux-adapted skill doc (vault at `~/obsidian-vault`, not `~/Library/...`)

### Modified files
- `deploy-tier2.sh` — add `--obsidian-repo` flag + two new positional args
- `roles/tier2-setup/tasks/install.yml` — new Phase 9p block
- `roles/tier2-setup/templates/tools.yaml.j2` — add vault path to allowedPaths; add `git`, `obsidian-cli` to shell allowlist
- `roles/tier2-setup/templates/exec-approvals.json.j2` — add `obsidian-cli` binary path to dev agent allowlist

---

## Implementation Detail

### 1. `deploy-tier2.sh`
Add parsing:
```bash
--obsidian-repo) OBSIDIAN_REPO="$2"; shift ;;
```
Extend Python extra-vars to `sys.argv[28]`:
- `[27]` = `obsidian_repo_slug`
- `[28]` = `obsidian_vault_name` (defaults to repo name extracted from slug if empty)

Add validation: if `--obsidian-repo` is set, no other flags are required (vault name is optional, defaults to repo basename).

### 2. `install.yml` — Phase 9p (after Phase 9o)

Gate all tasks on: `when: obsidian_repo_slug | default('') | length > 0`

Tasks in order:
1. **Install obsidian-cli globally**: `npm install -g obsidian-cli` (run as root; check if already installed via `which obsidian-cli`, `changed_when` on install)
2. **Deploy key generation**: `ssh-keygen -t ed25519` to `~openclaw/.ssh/openclaw-obsidian-deploy` — gated on `not deploy_key_stat.stat.exists` (same idempotency pattern as scripts-repo)
3. **Display public key + pause** (gated on key not existing, same pause task pattern)
4. **Git clone** vault to `~/obsidian-vault/` — uses the deploy key via `GIT_SSH_COMMAND`
5. **Create `~/.config/obsidian/` directory**
6. **Write `~/.config/obsidian/obsidian.json`**: registers vault with its name + absolute path
7. **Run `obsidian-cli set-default "{{ obsidian_vault_name }}"`** — idempotent
8. **Create skills/obsidian/ directory** and deploy SKILL.md
9. **System cron** (in `/etc/cron.d/openclaw-obsidian`):
   - Every hour at `:05` — `git -C ~/obsidian-vault pull --ff-only origin main`
   - Every hour at `:20` — auto-commit + push any pending agent writes: `git -C ~/obsidian-vault add . && git diff --cached --quiet || git commit -m "auto: agent sync" && git push`

### 3. `SKILL.md` (Linux-adapted)

Key adaptations vs upstream:
- Vault path is `~/obsidian-vault/` (not autodiscovered from `~/Library/`)
- After any write operation, instruct agent to run: `git -C ~/obsidian-vault add . && git commit -m "<reason>" && git push`
- Pull before read sessions: `git -C ~/obsidian-vault pull --ff-only origin main`

Sections: overview, commands (search, search-content, create, move, delete), git sync instructions, safety rules (no force push, commit messages describe what changed).

### 4. `tools.yaml.j2`

Add to `filesystem.allowedPaths` (gated on obsidian being configured):
```yaml
{% if obsidian_repo_slug | default('') | length > 0 %}
- /home/{{ openclaw_user }}/obsidian-vault
{% endif %}
```

Add to `shell.allowlist`:
- `git` (needed for pull/commit/push from skill)
- `obsidian-cli` (already installed globally)

### 5. `exec-approvals.json.j2`

Add to `agents.dev.allowlist`:
```json
{ "pattern": "/usr/bin/git" },
{ "pattern": "/usr/bin/obsidian-cli" }
```
(Use a `register` task to get the actual path from `which obsidian-cli` during deploy, similar to how `openclaw_bin.stdout` is captured.)

---

## Sync Conflict Strategy

- **Pull cron runs at `:05`** — before the auto-commit at `:20`, so the agent's writes always sit on top of latest remote
- **Agent is instructed to pull before starting a multi-note editing session** (in SKILL.md)
- **No force push ever** — SKILL.md explicitly forbids it
- **Conflict scenario** (agent edits + local edit simultaneously): git pull at `:05` may fail with merge conflict — cron should log failures to `~/obsidian-vault-sync.log`; alerts via `openclaw message send` if pull fails 3× in a row (optional stretch goal, not in initial impl)

---

## Verification

1. `ansible-playbook playbook-tier2.yml --syntax-check` — no parse errors
2. Deploy to a test target with `--obsidian-repo user/vault`:
   - Verify deploy key generated at `~openclaw/.ssh/openclaw-obsidian-deploy`
   - Verify vault cloned to `~/obsidian-vault/`
   - Verify `~/.config/obsidian/obsidian.json` exists and contains correct vault entry
   - Verify `obsidian-cli print-default --path-only` returns `~/obsidian-vault`
   - Verify SKILL.md deployed to `~/workspace/skills/obsidian/SKILL.md`
   - Verify cron entries in `/etc/cron.d/openclaw-obsidian`
3. Re-deploy (idempotency check): deploy key not regenerated, vault not re-cloned, no duplicate cron entries
4. Agent smoke test: ask agent to search for a note by name, create a new test note, verify it appears in the git log
