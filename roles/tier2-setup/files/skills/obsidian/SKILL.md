# Obsidian Vault

Provides read/write access to the user's Obsidian vault at `~/obsidian-vault/`.
The vault is a plain markdown file tree synced via git.

## Mandatory Safety Rules

- NEVER write to or modify anything inside `~/obsidian-vault/.obsidian/` — this
  folder contains Obsidian's plugin configs and workspace state. Touching it corrupts
  the desktop/mobile apps.
- NEVER force-push (`git push --force`).
- Commit messages must describe what changed (e.g. "add note on X", "update Y").
- Pull before starting any multi-note editing session.

## Git Sync

**Before a read or edit session** (pull latest from remote):
```
GIT_SSH_COMMAND="ssh -i ~/.ssh/openclaw-obsidian-deploy" git -C ~/obsidian-vault pull --ff-only origin main
```

**After creating or modifying notes** (commit and push):
```
git -C ~/obsidian-vault add .
git -C ~/obsidian-vault diff --cached --quiet || git -C ~/obsidian-vault commit -m "<reason>"
GIT_SSH_COMMAND="ssh -i ~/.ssh/openclaw-obsidian-deploy" git -C ~/obsidian-vault push
```

An hourly cron handles background sync automatically (pull at :05, push at :20),
but always push explicitly after deliberate writes so changes arrive immediately.

## Search Notes by Name

```
find ~/obsidian-vault -name "*.md" | grep -i "keyword"
```

Exclude `.obsidian/` from results:
```
find ~/obsidian-vault -name "*.md" -not -path "*/.obsidian/*" | grep -i "keyword"
```

## Search Note Content (Full-Text)

List files containing the search term:
```
grep -r "keyword" ~/obsidian-vault --include="*.md" --exclude-dir=".obsidian" -l
```

Show matches with context:
```
grep -r "keyword" ~/obsidian-vault --include="*.md" --exclude-dir=".obsidian" -n -C 2
```

## Read a Note

```
cat ~/obsidian-vault/path/to/Note Name.md
```

List all notes in a folder:
```
find ~/obsidian-vault/FolderName -name "*.md" -not -path "*/.obsidian/*"
```

## Create a Note

Notes are plain markdown files. Use the `.md` extension and match Obsidian's naming
conventions for the vault (usually title-cased, spaces allowed).

Recommended frontmatter for agent-created notes:
```markdown
---
created: 2026-03-22
tags: []
---

Note content here.
```

Write the file, then commit and push (see Git Sync above).

## Move or Rename a Note

```
mv ~/obsidian-vault/OldName.md ~/obsidian-vault/NewName.md
```

**Warning:** this does NOT auto-update `[[OldName]]` wikilinks elsewhere in the vault.
After renaming, search for existing links and update them manually:
```
grep -r "OldName" ~/obsidian-vault --include="*.md" -l
```

Then edit each file to replace `[[OldName]]` with `[[NewName]]`.

## Delete a Note

```
rm ~/obsidian-vault/path/to/Note Name.md
```

Then commit and push. Check for wikilinks that reference this note beforehand:
```
grep -r "Note Name" ~/obsidian-vault --include="*.md" -l
```

## AI Processing

To ask the agent to fetch and summarize all links in a note, add this to
the note's frontmatter:

```yaml
ai_summarize: true
```

Commit and push the note. Within ~15 minutes (after the :05 pull + :15 cron)
the agent will:
- Fetch each URL in the note using `bash ~/scripts/fetch-url-content.sh <URL>`
- Append a `## AI Link Summaries` section with 2-4 sentence summaries per link
- Change `ai_summarize: true` to `ai_summarize: done` in the frontmatter
- Commit and push the updated note back to the vault

Notes with `ai_summarize: done` are not re-processed.

## Vault Structure

```
~/obsidian-vault/
├── .obsidian/          ← DO NOT TOUCH — Obsidian app config
├── .git/               ← git repo
├── FolderName/
│   └── Note.md
└── Note.md
```

Notes use `[[wikilinks]]` to link to each other by title (without `.md` extension).
Tags are either inline `#tag` or in frontmatter `tags: [tag1, tag2]`.
