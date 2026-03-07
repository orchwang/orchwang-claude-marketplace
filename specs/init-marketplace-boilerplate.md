# Plan: Boilerplate orchwang-claude-marketplace

## Context

The `orchwang-claude-marketplace` repository is an empty git repo that needs to be bootstrapped as a private Claude Code plugin marketplace for the **orchwang** GitHub user. The structure is benchmarked from `synapse-claude-marketplace` (datamaker-kr). The first plugin, `orchwang-general`, will be an empty skeleton.

## Files to Create

### Root-level files (7 files)

1. **`.claude-plugin/plugin.json`** — Marketplace manifest
   - name: `orchwang-marketplace`
   - version: `1.0.0`
   - author: orchwang
   - repo: `https://github.com/orchwang/orchwang-claude-marketplace`
   - Register `orchwang-general` plugin

2. **`README.md`** — Marketplace documentation (Korean)
   - Overview, quick start, plugin catalog table
   - orchwang-general section (empty placeholder)
   - Requirements (Claude Code v2.1.0+, GITHUB_TOKEN)
   - Troubleshooting, license

3. **`AGENTS.md`** — Repository guidelines
   - Project structure rules
   - Build/test commands
   - Coding style (kebab-case, YAML 2-space indent, Korean docs)
   - Commit/PR guidelines
   - Plugin documentation requirements

4. **`CLAUDE.md`** — Points to AGENTS.md (single line: `See [AGENTS.md](AGENTS.md).`)

5. **`CHANGELOG.md`** — Keep a Changelog format
   - `[1.0.0]` entry: marketplace initialization, orchwang-general plugin registered

6. **`.gitignore`** — Same pattern as reference (OS, IDE, Node, Python, logs, .env, specs, .claude/settings.local.json)

7. **`docs/CONTRIBUTING.md`** — Contribution guide
   - Adapted for orchwang/orchwang-claude-marketplace
   - Plugin structure rules, naming conventions, review process

### Plugin: orchwang-general (empty skeleton, 2 files)

8. **`plugins/orchwang-general/plugin.json`** — Plugin manifest
   ```json
   {
     "name": "orchwang-general",
     "version": "1.0.0",
     "description": "General-purpose Claude Code plugin for orchwang projects",
     "author": { "name": "orchwang" },
     "homepage": "https://github.com/orchwang/orchwang-claude-marketplace",
     "repository": "https://github.com/orchwang/orchwang-claude-marketplace.git",
     "license": "MIT",
     "keywords": ["orchwang", "general", "development"],
     "commands": [],
     "skills": [],
     "agents": []
   }
   ```

9. **`plugins/orchwang-general/README.md`** — Plugin README (Korean)
   - Minimal skeleton with required sections (overview, install, commands, skills, agents, quick start, license)
   - All sections marked as "추가 예정" (to be added)

### Empty directories to establish structure

10. **`plugins/orchwang-general/commands/.gitkeep`**
11. **`plugins/orchwang-general/skills/.gitkeep`**
12. **`plugins/orchwang-general/agents/.gitkeep`**

### Total: 12 files

## Key Adaptations from Reference

| Aspect | synapse-claude-marketplace | orchwang-claude-marketplace |
|--------|---------------------------|----------------------------|
| Owner | datamaker-kr (org) | orchwang (user) |
| Repo URL | datamaker-kr/synapse-claude-marketplace | orchwang/orchwang-claude-marketplace |
| Marketplace name | synapse-marketplace | orchwang-marketplace |
| License | MIT | MIT |
| Doc language | Korean | Korean |
| Initial plugins | 6 mature plugins | 1 empty plugin (orchwang-general) |
| MCP config (.mcp.json) | Included | Omitted (no MCP servers needed yet) |
| .env | Included | Omitted (avoid committing secrets) |

## Execution Order

1. Create root config files: `.gitignore`, `CLAUDE.md`, `AGENTS.md`
2. Create `.claude-plugin/plugin.json`
3. Create `plugins/orchwang-general/` structure (plugin.json, README.md, .gitkeep files)
4. Create root `README.md`, `CHANGELOG.md`
5. Create `docs/CONTRIBUTING.md`

## Verification

1. Run `ls -R` to confirm full directory structure
2. Validate `plugin.json` files are valid JSON: `cat .claude-plugin/plugin.json | python3 -m json.tool`
3. Confirm no secrets committed: check `.gitignore` excludes `.env`
4. Test plugin locally: `claude --plugin-dir .` (from marketplace root)
