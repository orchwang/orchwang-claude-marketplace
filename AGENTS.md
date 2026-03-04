# Repository Guidelines

## Project Structure & Module Organization
- `.claude-plugin/plugin.json` defines marketplace metadata used by Claude Code.
- Each plugin lives under `plugins/<plugin-name>/` with its own `plugin.json`.
- `commands/` contains slash-command specs (`*.md`) with YAML frontmatter and step-by-step workflows.
- `skills/` holds skill modules; each `skills/<skill>/SKILL.md` may link to `skills/<skill>/references/`.
- `agents/` provides autonomous agent playbooks invoked by the plugin.
- `docs/` stores supporting documentation for contribution and onboarding.

## Build, Test, and Development Commands
- `claude --plugin-dir .` runs this marketplace locally in Claude Code for manual verification.
- No automated test suite exists; validate changes by running the relevant slash command in Claude Code.

## Coding Style & Naming Conventions
- Markdown is the primary format; keep YAML frontmatter at the top of command files.
- Use kebab-case for plugin codes and folder names (e.g., `my-plugin`).
- Keep instructions direct and deterministic; prefer numbered steps and fenced code blocks for commands.
- Use 2-space indentation in YAML examples and align tables for readability.
- Documentation language: Korean.

## Commit & Pull Request Guidelines
- Use short, imperative commit messages (e.g., `docs: update README`, `feat: add orchwang-general plugin`).
- PRs should include: a brief summary, related issue link (if any), and commands run.
- If you change command behavior, update `README.md` and the corresponding file in `commands/`.

## Plugin Documentation Requirements
- Every plugin must have a `plugin.json` manifest and `README.md`.
- README must include: overview, installation, commands, skills, agents, quick start, and license sections.
- Keep plugin descriptions concise and in Korean.

## Security & Configuration Tips
- Do not commit secrets; reference env vars in examples instead.
- Keep `plugin.json` metadata accurate and avoid introducing local paths or credentials.
