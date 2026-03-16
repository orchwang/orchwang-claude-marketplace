#!/usr/bin/env python3
"""Claude to Codex migration script.

Converts .claude/ assets (commands, skills, rules, docs, plugins) into
Codex-compatible skill directories.

Usage:
    python migrate.py [OPTIONS] [PROJECT_ROOT]

Requires Python 3.10+ standard library only (no external dependencies).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from textwrap import shorten

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIZE_THRESHOLD_BYTES = 40_000  # ~10k tokens
ACRONYMS = {"pr", "api", "cli", "url", "http", "json", "yaml", "tdd", "sdd", "mcp"}
PLUGIN_EXCLUDE_FILES = {"plugin.json", "README.md", "CLAUDE.md"}
PLUGIN_EXCLUDE_DIRS = {"specs"}
PLUGIN_EXCLUDE_PATTERNS = {"LICENSE"}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MigrationItem:
    source: str
    targets: list[str]
    item_type: str   # command | skill | rules | docs | plugin-agent | plugin-skill | plugin-command
    status: str      # new | conflict | skip | error | created | needs-llm-review
    action: str      # script | llm
    notes: str | None = None


# ---------------------------------------------------------------------------
# Frontmatter parser (no PyYAML)
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---[ \t]*\n(.*?\n)---[ \t]*\n", re.DOTALL)
_KV_RE = re.compile(r"^([\w][\w-]*)\s*:\s*(.+)$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body) from a markdown file with YAML front matter."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    fm = {}
    for kv in _KV_RE.finditer(raw):
        key = kv.group(1).strip()
        val = kv.group(2).strip().strip("\"'")
        fm[key] = val
    body = text[m.end():]
    return fm, body


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def slugify_name(name: str) -> str:
    """Convert *name* to Codex-valid hyphen-case (lowercase, a-z0-9 and hyphens)."""
    s = name.lower().replace(" ", "-").replace("_", "-")
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s[:64]


def to_title_case(name: str) -> str:
    """Convert hyphen-case name to Title Case with acronym handling."""
    parts = name.split("-")
    result = []
    for p in parts:
        if p.lower() in ACRONYMS:
            result.append(p.upper())
        else:
            result.append(p.capitalize())
    return " ".join(result)


def truncate_description(desc: str, max_len: int = 1024) -> str:
    """Remove angle brackets and truncate to *max_len*."""
    desc = re.sub(r"[<>]", "", desc)
    if len(desc) > max_len:
        desc = shorten(desc, width=max_len, placeholder="...")
    return desc


def make_short_description(desc: str) -> str:
    """Return a 25-64 char short description suitable for openai.yaml."""
    cleaned = truncate_description(desc, 64)
    if len(cleaned) < 25:
        cleaned = cleaned.ljust(25)
    return cleaned


def generate_openai_yaml(name: str, description: str) -> str:
    display = to_title_case(name)
    short = make_short_description(description)
    return (
        "interface:\n"
        f'  display_name: "{display}"\n'
        f'  short_description: "{short}"\n'
    )


def write_skill_dir(
    output_dir: Path,
    name: str,
    description: str,
    body: str,
    *,
    large: bool = False,
    extra_refs: dict[str, str] | None = None,
) -> None:
    """Create a Codex skill directory with SKILL.md, agents/openai.yaml, and optional references."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "agents").mkdir(exist_ok=True)

    # SKILL.md
    if large:
        (output_dir / "references").mkdir(exist_ok=True)
        (output_dir / "references" / "full-workflow.md").write_text(body, encoding="utf-8")
        skill_body = (
            f"This skill's full workflow is large. "
            f"For detailed steps, read `references/full-workflow.md`.\n\n"
            f"<!-- LLM: Replace this placeholder with a concise summary of the workflow. -->\n"
        )
    else:
        skill_body = body

    skill_content = f"---\nname: {name}\ndescription: {truncate_description(description)}\n---\n\n{skill_body}"
    (output_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

    # agents/openai.yaml
    (output_dir / "agents" / "openai.yaml").write_text(
        generate_openai_yaml(name, description), encoding="utf-8"
    )

    # extra references
    if extra_refs:
        refs_dir = output_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        for ref_name, ref_content in extra_refs.items():
            (refs_dir / ref_name).write_text(ref_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Plugin configuration
# ---------------------------------------------------------------------------

def load_plugin_config(project_root: Path, args: argparse.Namespace) -> list[str]:
    """Return list of plugin names to migrate.  CLI > config file > empty."""
    if getattr(args, "plugins", None):
        return list(args.plugins)

    config_path = project_root / ".claude" / "codex-migration.json"
    if config_path.is_file():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            plugins = data.get("plugins", [])
            if isinstance(plugins, list):
                return [str(p) for p in plugins]
        except (json.JSONDecodeError, KeyError):
            print(f"WARNING: Failed to parse {config_path}, ignoring plugin config", file=sys.stderr)
    return []


def resolve_plugin_paths(plugin_names: list[str]) -> dict[str, Path]:
    """Resolve plugin names to installed paths via installed_plugins.json."""
    installed_path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not installed_path.is_file():
        print(f"WARNING: {installed_path} not found, skipping plugins", file=sys.stderr)
        return {}

    try:
        data = json.loads(installed_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Failed to read {installed_path}, skipping plugins", file=sys.stderr)
        return {}

    # Format: {"version": 2, "plugins": {"name@marketplace": [{"installPath": "...", ...}]}}
    plugins_map = data.get("plugins", data) if isinstance(data, dict) else {}

    result: dict[str, Path] = {}
    for key, entries in plugins_map.items():
        if not isinstance(entries, list):
            continue
        # Extract plugin name from "name@marketplace" key
        plugin_key_name = key.split("@")[0] if "@" in key else key
        if plugin_key_name not in plugin_names:
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            install_path = entry.get("installPath", "")
            if install_path:
                p = Path(install_path).expanduser()
                if p.is_dir():
                    result[plugin_key_name] = p
                else:
                    print(f"WARNING: Plugin '{plugin_key_name}' install path does not exist: {p}", file=sys.stderr)
                break  # use first matching entry

    for pn in plugin_names:
        if pn not in result:
            print(f"WARNING: Plugin '{pn}' not found in installed plugins", file=sys.stderr)

    return result


# ---------------------------------------------------------------------------
# Conversion functions
# ---------------------------------------------------------------------------

def convert_commands(claude_dir: Path, args: argparse.Namespace) -> list[MigrationItem]:
    """Convert .claude/commands/*.md → Codex skill directories."""
    commands_dir = claude_dir / "commands"
    if not commands_dir.is_dir():
        return []

    items: list[MigrationItem] = []
    for md_file in sorted(commands_dir.glob("*.md")):
        items.append(_convert_single_md(
            md_file=md_file,
            base_dir=claude_dir.parent,
            output_base=Path(args.output_dir),
            item_type="command",
            name_prefix="",
            dry_run=args.dry_run,
            force=args.force,
        ))
    return items


def convert_skills(claude_dir: Path, args: argparse.Namespace) -> list[MigrationItem]:
    """Convert .claude/skills/*.md → Codex skill directories."""
    skills_dir = claude_dir / "skills"
    if not skills_dir.is_dir():
        return []

    items: list[MigrationItem] = []
    for md_file in sorted(skills_dir.glob("*.md")):
        items.append(_convert_single_md(
            md_file=md_file,
            base_dir=claude_dir.parent,
            output_base=Path(args.output_dir),
            item_type="skill",
            name_prefix="",
            dry_run=args.dry_run,
            force=args.force,
        ))
    return items


def _convert_single_md(
    *,
    md_file: Path,
    base_dir: Path,
    output_base: Path,
    item_type: str,
    name_prefix: str,
    dry_run: bool,
    force: bool,
) -> MigrationItem:
    """Shared logic for converting a single .md file (command or skill)."""
    text = md_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    raw_name = fm.get("name", md_file.stem)
    name = slugify_name(f"{name_prefix}{raw_name}" if name_prefix else raw_name)
    desc = fm.get("description", "")
    out_dir = output_base / name
    large = len(text.encode("utf-8")) >= SIZE_THRESHOLD_BYTES

    targets = [str(out_dir / "SKILL.md"), str(out_dir / "agents" / "openai.yaml")]
    if large:
        targets.append(str(out_dir / "references" / "full-workflow.md"))

    status = "conflict" if out_dir.exists() and not force else "new"

    if not dry_run and status != "conflict":
        write_skill_dir(out_dir, name, desc, body, large=large)
        status = "created"

    try:
        source_rel = str(md_file.relative_to(base_dir))
    except ValueError:
        source_rel = str(md_file)

    return MigrationItem(
        source=source_rel,
        targets=targets,
        item_type=item_type,
        status=status,
        action="script",
        notes="large file → references/" if large else None,
    )


def convert_rules(project_root: Path, args: argparse.Namespace) -> list[MigrationItem]:
    """Copy P1-P4 rules into code-review skill's references/ directory."""
    items: list[MigrationItem] = []
    rule_files = sorted(project_root.glob("P[1-4]_rules.md"))
    if not rule_files:
        return items

    code_review_dir = Path(args.output_dir) / "code-review"
    refs_dir = code_review_dir / "references"

    for rf in rule_files:
        target = refs_dir / rf.name
        targets = [str(target)]
        status = "conflict" if target.exists() and not args.force else "new"

        if not args.dry_run and status != "conflict":
            refs_dir.mkdir(parents=True, exist_ok=True)
            # Ensure code-review skill exists (minimal if not already created)
            if not (code_review_dir / "SKILL.md").exists():
                write_skill_dir(
                    code_review_dir,
                    "code-review",
                    "Code review using P1-P4 priority rules",
                    "Review code changes using the P1-P4 rule files in references/.\n",
                )
            shutil.copy2(rf, target)
            status = "created"

        items.append(MigrationItem(
            source=str(rf.relative_to(project_root)),
            targets=targets,
            item_type="rules",
            status=status,
            action="script",
        ))
    return items


def analyze_docs(project_root: Path, args: argparse.Namespace) -> list[MigrationItem]:
    """Analyze CLAUDE.md / AGENTS.md for Codex compatibility."""
    items: list[MigrationItem] = []
    claude_md = project_root / "CLAUDE.md"
    agents_md = project_root / "AGENTS.md"

    if not claude_md.is_file() and not agents_md.is_file():
        return items

    if agents_md.is_file():
        items.append(MigrationItem(
            source="AGENTS.md",
            targets=[],
            item_type="docs",
            status="skip",
            action="script",
            notes="AGENTS.md is natively supported by Codex — no conversion needed",
        ))

    if claude_md.is_file():
        content = claude_md.read_text(encoding="utf-8")
        is_reference_only = bool(re.search(r"(?i)see\s+\[?AGENTS\.md", content)) and len(content.strip()) < 200
        if is_reference_only:
            status = "skip"
            notes = "CLAUDE.md is a simple reference to AGENTS.md — skip"
        elif agents_md.is_file():
            status = "needs-llm-review"
            notes = "CLAUDE.md has additional content beyond AGENTS.md reference — LLM should review and merge"
        else:
            status = "needs-llm-review"
            notes = "Only CLAUDE.md exists (no AGENTS.md) — consider copying to AGENTS.md"
        items.append(MigrationItem(
            source="CLAUDE.md",
            targets=[],
            item_type="docs",
            status=status,
            action="llm" if "llm" in status else "script",
            notes=notes,
        ))
    return items


def convert_plugins(plugin_names: list[str], args: argparse.Namespace) -> list[MigrationItem]:
    """Convert installed plugin agents/skills/commands → Codex skill directories."""
    paths = resolve_plugin_paths(plugin_names)
    if not paths:
        return []

    items: list[MigrationItem] = []
    output_base = Path(args.output_dir)

    for plugin_name, plugin_path in sorted(paths.items()):
        prefix = f"{slugify_name(plugin_name)}-"

        # Plugin agents (already SKILL.md format)
        agents_dir = plugin_path / "agents"
        if agents_dir.is_dir():
            for agent_dir in sorted(agents_dir.iterdir()):
                if not agent_dir.is_dir():
                    continue
                skill_md = agent_dir / "SKILL.md"
                if not skill_md.is_file():
                    continue
                items.append(_convert_plugin_skill_dir(
                    source_dir=agent_dir,
                    plugin_name=plugin_name,
                    prefix=prefix,
                    output_base=output_base,
                    item_type="plugin-agent",
                    dry_run=args.dry_run,
                    force=args.force,
                ))

        # Plugin skills (already SKILL.md format, may have auxiliary files)
        skills_dir = plugin_path / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(skills_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.is_file():
                    continue
                items.append(_convert_plugin_skill_dir(
                    source_dir=skill_dir,
                    plugin_name=plugin_name,
                    prefix=prefix,
                    output_base=output_base,
                    item_type="plugin-skill",
                    dry_run=args.dry_run,
                    force=args.force,
                ))

        # Plugin commands (same format as .claude/commands/)
        commands_dir = plugin_path / "commands"
        if commands_dir.is_dir():
            for md_file in sorted(commands_dir.glob("*.md")):
                items.append(_convert_single_md(
                    md_file=md_file,
                    base_dir=plugin_path,
                    output_base=output_base,
                    item_type="plugin-command",
                    name_prefix=prefix,
                    dry_run=args.dry_run,
                    force=args.force,
                ))

    return items


def _convert_plugin_skill_dir(
    *,
    source_dir: Path,
    plugin_name: str,
    prefix: str,
    output_base: Path,
    item_type: str,
    dry_run: bool,
    force: bool,
) -> MigrationItem:
    """Convert a plugin agent/skill directory (already has SKILL.md) to namespaced Codex skill."""
    skill_md = source_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    raw_name = fm.get("name", source_dir.name)
    name = slugify_name(f"{prefix}{raw_name}")
    desc = fm.get("description", "")
    out_dir = output_base / name

    targets = [str(out_dir / "SKILL.md"), str(out_dir / "agents" / "openai.yaml")]

    # Collect auxiliary files (templates, guidelines, etc.) for references/
    extra_refs: dict[str, str] = {}
    for child in sorted(source_dir.rglob("*")):
        if not child.is_file():
            continue
        if child.name == "SKILL.md":
            continue
        if child.name in PLUGIN_EXCLUDE_FILES:
            continue
        if any(child.name.startswith(pat) for pat in PLUGIN_EXCLUDE_PATTERNS):
            continue
        if any(part in PLUGIN_EXCLUDE_DIRS for part in child.relative_to(source_dir).parts):
            continue
        try:
            rel = str(child.relative_to(source_dir))
            # Flatten into references/ using path-as-name
            ref_name = rel.replace("/", "--")
            extra_refs[ref_name] = child.read_text(encoding="utf-8")
            targets.append(str(out_dir / "references" / ref_name))
        except (ValueError, UnicodeDecodeError):
            pass

    large = len(text.encode("utf-8")) >= SIZE_THRESHOLD_BYTES
    status = "conflict" if out_dir.exists() and not force else "new"

    if not dry_run and status != "conflict":
        write_skill_dir(out_dir, name, desc, body, large=large, extra_refs=extra_refs or None)
        status = "created"

    return MigrationItem(
        source=f"[plugin:{plugin_name}] {source_dir.name}/",
        targets=targets,
        item_type=item_type,
        status=status,
        action="script",
        notes=f"from plugin {plugin_name}" + (", large file → references/" if large else ""),
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(items: list[MigrationItem], args: argparse.Namespace) -> None:
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        _report_json(items, args)
    else:
        _report_text(items, args)


def _report_json(items: list[MigrationItem], args: argparse.Namespace) -> None:
    summary = _summarize(items)
    output = {
        "project_root": str(getattr(args, "project_root", ".")),
        "output_dir": str(args.output_dir),
        "dry_run": args.dry_run,
        "items": [asdict(it) for it in items],
        "summary": summary,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def _report_text(items: list[MigrationItem], args: argparse.Namespace) -> None:
    mode = "DRY-RUN" if args.dry_run else "MIGRATION"
    print(f"\n[{mode}] {'Migration Plan' if args.dry_run else 'Results'}")
    print("─" * 50)
    for it in items:
        print(f"\n  Source: {it.source}")
        for t in it.targets:
            tag = it.status.upper()
            print(f"    → {t}  [{tag}]")
        if it.notes:
            print(f"    Note: {it.notes}")

    s = _summarize(items)
    print(f"\n{'─' * 50}")
    print(f"  Summary: {s['total_sources']} sources | "
          f"{s['files_to_create']} to create | "
          f"{s['created']} created | "
          f"{s['conflicts']} conflicts | "
          f"{s['skips']} skips | "
          f"{s['errors']} errors | "
          f"{s['needs_llm_review']} need LLM review")
    print()


def _summarize(items: list[MigrationItem]) -> dict[str, int]:
    return {
        "total_sources": len(items),
        "files_to_create": sum(len(it.targets) for it in items if it.status in ("new", "created")),
        "created": sum(1 for it in items if it.status == "created"),
        "conflicts": sum(1 for it in items if it.status == "conflict"),
        "skips": sum(1 for it in items if it.status == "skip"),
        "errors": sum(1 for it in items if it.status == "error"),
        "needs_llm_review": sum(1 for it in items if it.status == "needs-llm-review"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Migrate Claude Code (.claude/) assets to Codex-compatible skill format.",
    )
    p.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )
    p.add_argument("--output-dir", default=None, help="Output directory (default: {PROJECT_ROOT}/.codex/skills/)")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without creating files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    p.add_argument("--skip-rules", action="store_true", help="Skip P1-P4 rules conversion")
    p.add_argument("--skip-docs", action="store_true", help="Skip CLAUDE.md/AGENTS.md analysis")
    p.add_argument("--skip-plugins", action="store_true", help="Skip plugin assets conversion")
    p.add_argument("--plugins", nargs="+", metavar="NAME", help="Plugin names to convert (overrides config file)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Report output format")
    args = p.parse_args(argv)

    # Resolve project root
    args.project_root = str(Path(args.project_root).resolve())
    if args.output_dir is None:
        args.output_dir = str(Path(args.project_root) / ".codex" / "skills")
    else:
        args.output_dir = str(Path(args.output_dir).resolve())

    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root)
    claude_dir = project_root / ".claude"

    if not claude_dir.is_dir():
        print(f"ERROR: .claude/ directory not found in {project_root}", file=sys.stderr)
        return 2

    items: list[MigrationItem] = []
    items.extend(convert_commands(claude_dir, args))
    items.extend(convert_skills(claude_dir, args))

    if not args.skip_rules:
        items.extend(convert_rules(project_root, args))

    if not args.skip_docs:
        items.extend(analyze_docs(project_root, args))

    if not args.skip_plugins:
        plugin_names = load_plugin_config(project_root, args)
        if plugin_names:
            items.extend(convert_plugins(plugin_names, args))

    generate_report(items, args)

    errors = sum(1 for it in items if it.status == "error")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
