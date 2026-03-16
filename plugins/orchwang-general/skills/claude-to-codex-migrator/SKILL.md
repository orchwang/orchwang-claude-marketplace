---
name: claude-to-codex-migrator
description: Migrate Claude Code (.claude/) assets to Codex-compatible skill format. Use when setting up a project that has existing Claude Code configuration (commands, skills, rules, plugins) for use with Codex CLI.
---

# Claude to Codex Migrator

This skill converts Claude Code assets into Codex-compatible skill format:
- `.claude/commands/*.md` → individual Codex skill directories
- `.claude/skills/*.md` → individual Codex skill directories (with progressive disclosure for large files)
- `P1-P4_rules.md` → code-review skill references
- `CLAUDE.md` / `AGENTS.md` → compatibility analysis
- Installed plugin agents, skills, and commands → namespaced Codex skills

## Phase 1: Structural Conversion (Script)

Run the migration script to perform deterministic conversions.

### Step 1: Preview with dry-run

```
python ~/.codex/skills/claude-to-codex-migrator/scripts/migrate.py . --dry-run
```

Review the output to see what will be converted and check for conflicts.

### Step 2: Run the migration

```
python ~/.codex/skills/claude-to-codex-migrator/scripts/migrate.py .
```

This creates Codex skill directories in `.codex/skills/` by default.

### Options

- `--output-dir PATH` — custom output directory
- `--force` — overwrite existing files
- `--skip-rules` — skip P1-P4 rules conversion
- `--skip-docs` — skip CLAUDE.md/AGENTS.md analysis
- `--skip-plugins` — skip plugin assets conversion
- `--plugins NAME [...]` — convert specific plugins (overrides `.claude/codex-migration.json`)
- `--format json` — machine-readable output

### Plugin Configuration

To include installed Claude plugins in the migration, either:

1. Create `.claude/codex-migration.json`:
   ```json
   {"plugins": ["platform-dev-team-common", "sdd-helper"]}
   ```

2. Or pass plugin names via CLI:
   ```
   python ~/.codex/skills/claude-to-codex-migrator/scripts/migrate.py . --plugins sdd-helper
   ```

## Phase 2: Content Rewriting (LLM)

After Phase 1 completes, review and improve the converted skills.

### For each converted SKILL.md:

1. **Read** the converted SKILL.md file
2. **Rewrite** the body to be natural Codex instructions:
   - Remove Claude-specific patterns like `$ARGUMENTS` — instead describe what
     input the skill expects from the user in natural language
   - Replace `.claude/skills/` path references with the new skill locations
   - Ensure the `description` field clearly states WHEN to trigger the skill
     (this is critical for Codex skill discovery)
3. **Validate** the format:
   ```
   python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py {skill_dir}
   ```

### For large skills with references/:

1. **Read** `references/full-workflow.md`
2. **Write** a concise summary in the SKILL.md body that:
   - Describes the overall workflow purpose
   - Lists key steps at a high level
   - References the detailed workflow: "For detailed steps, read `references/full-workflow.md`"

### For CLAUDE.md / AGENTS.md (if flagged as needs-llm-review):

1. **Read** both files
2. **Decide** whether to merge CLAUDE.md content into AGENTS.md or create a
   separate instructions file
3. **Apply** the decision

## Reference

For detailed format mapping between Claude and Codex, read:
`references/format-mapping.md`
