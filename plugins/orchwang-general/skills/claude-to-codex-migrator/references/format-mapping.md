# Claude ↔ Codex Format Mapping Reference

## Claude Command Format

**Location**: `.claude/commands/{name}.md`

```yaml
---
name: command-name
description: Brief description
---
```

Body: Markdown with `$ARGUMENTS` placeholder for user input.

### Key Patterns
- `$ARGUMENTS` — replaced at runtime with user-provided arguments
- References to `.claude/skills/` files for workflow delegation
- YAML frontmatter: only `name` and `description` fields

## Claude Skill Format

**Location**: `.claude/skills/{name}.md`

```yaml
---
name: skill-name
description: Brief description
---
```

Body: Step-by-step workflow instructions with numbered steps, git commands, PR templates, user confirmation points.

### Key Patterns
- `$ARGUMENTS` — parsed for flags like `--type`, `--lang`
- "Arguments to parse" section listing expected inputs
- Workflow Steps with sequential numbering
- References to other skill files (e.g., `.claude/skills/release-to-staging.md`)

## Claude Plugin Format

**Location**: `~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/`

```
{plugin}/
├── agents/{agent-name}/SKILL.md     # Agent definition (already SKILL.md format!)
├── skills/{skill-name}/SKILL.md     # Skill definition (already SKILL.md format!)
├── skills/{skill-name}/templates/   # Auxiliary files
├── commands/{command-name}.md       # Same format as .claude/commands/
├── plugin.json                      # Plugin metadata (NOT converted)
├── README.md                        # Documentation (NOT converted)
└── CLAUDE.md                        # Plugin instructions (NOT converted)
```

Note: Plugin agents and skills already use `SKILL.md` + directory structure, similar to Codex.

## Codex SKILL.md Format

**Location**: `~/.codex/skills/{skill-name}/SKILL.md`

```yaml
---
name: skill-name
description: What the skill does and WHEN to use it (critical for triggering)
---
```

### Required Fields
- `name`: lowercase hyphen-case, max 64 characters, no leading/trailing hyphens, no consecutive hyphens
- `description`: max 1024 characters, no angle brackets `<` or `>`

### Optional Fields
- `license`: License identifier
- `allowed-tools`: Tools the skill requires
- `metadata`: Additional metadata

### Body
Natural language instructions for the LLM. Key principles:
- Progressive disclosure: metadata → SKILL.md body → bundled resources
- Context efficiency: only essential information
- Reference large content via `references/` directory

## Codex agents/openai.yaml Format

```yaml
interface:
  display_name: "Human Readable Name"
  short_description: "25-64 character description"
  icon_small: "./assets/icon-small.svg"    # optional
  icon_large: "./assets/icon-large.png"    # optional
  brand_color: "#hex"                       # optional
  default_prompt: "prompt text"             # optional
```

## Codex Validation Rules

Enforced by `quick_validate.py`:
- `SKILL.md` must exist in skill root directory
- Valid YAML frontmatter between `---` markers
- `name` field: regex `^[a-z0-9-]+$`, max 64 chars, no leading/trailing/consecutive hyphens
- `description` field: max 1024 chars, no angle brackets
- Only allowed frontmatter keys: `name`, `description`, `license`, `allowed-tools`, `metadata`

## Conversion Rules

### Name Conversion
- Already hyphen-case → keep as-is
- Contains spaces → replace with hyphens
- Contains uppercase → lowercase
- Contains special chars → remove (`[^a-z0-9-]`)
- Consecutive hyphens → single hyphen
- Leading/trailing hyphens → remove

### Description Conversion
- Remove angle brackets `<` and `>`
- Truncate to 1024 characters if longer
- Preserve meaning when truncating (cut at word boundary)

### Display Name Generation (for openai.yaml)
- Hyphen-case → Title Case
- Known acronyms kept uppercase: API, PR, CLI, URL, HTTP, JSON, YAML, TDD, SDD, MCP

### Short Description (for openai.yaml)
- Extract from description, 25-64 character range
- Cut at word boundary if needed

### $ARGUMENTS Pattern
- Claude uses `$ARGUMENTS` as a runtime placeholder
- Codex skills receive input differently (user prompt context)
- Conversion: describe expected inputs in natural language instead
- Example: `$ARGUMENTS` → "The user will provide the base branch and language as arguments"

### Path Reference Updates
- `.claude/skills/{name}.md` → reference the converted skill by its new name
- `.claude/commands/{name}.md` → reference the converted skill by its new name

### Progressive Disclosure (Large Files)
- Threshold: ~40KB file size (≈10k tokens)
- Below threshold: full body in SKILL.md
- Above threshold: summary in SKILL.md + full content in `references/full-workflow.md`

## Plugin Conversion Rules

### Namespace Prefix
All plugin assets get `{plugin-name}-` prefix to avoid name collisions:
- `sdd-helper` plugin's `init-specs` → `sdd-helper-init-specs`
- `platform-dev-team-common` plugin's `commit-with-message` → `platform-dev-team-common-commit-with-message`

### Plugin Assets Already in SKILL.md Format
Plugin agents and skills already have `SKILL.md` files → minimal conversion needed:
1. Copy directory structure
2. Update frontmatter `name` with prefix
3. Move auxiliary files (templates/, README.md) to `references/`

### Plugin Commands
Same conversion as project `.claude/commands/` (see above), with name prefix.

### Excluded Plugin Files
- `plugin.json` — metadata, not relevant to Codex
- `README.md` — documentation, not a skill
- `LICENSE*.md` — license files
- `specs/` — specification documents

## P1-P4 Rules Mapping

### Why NOT .codex/rules/
Codex `.rules` files use `prefix_rule(pattern=..., decision=...)` format for command prefix
allow/deny decisions. This is semantically different from code review guidelines.

### Strategy: code-review skill references/
P1-P4 rule files are copied verbatim into the code-review skill's `references/` directory:
```
code-review/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── P1_rules.md    # Critical - Security and Stability
    ├── P2_rules.md    # High - Core Functionality
    ├── P3_rules.md    # Medium - Best Practices
    └── P4_rules.md    # Low - Code Style
```

## CLAUDE.md / AGENTS.md Compatibility

| Scenario | Action |
|----------|--------|
| CLAUDE.md is just `See AGENTS.md` reference | Skip — AGENTS.md is Codex-native |
| CLAUDE.md has additional content beyond reference | Flag for LLM review — merge into AGENTS.md or create separate file |
| Only CLAUDE.md exists, no AGENTS.md | Flag as action-required — suggest copying to AGENTS.md |
| Only AGENTS.md exists | Skip — already Codex-compatible |
