# orchwang-general

orchwang 프로젝트를 위한 범용 Claude Code 플러그인입니다.

## 개요

이 플러그인은 orchwang 프로젝트 개발에 필요한 공통 도구를 제공합니다.

## 설치

```bash
/plugin install orchwang-general@orchwang-marketplace
```

## 명령어 (Commands)

추가 예정

## 스킬 (Skills)

### claude-to-codex-migrator

Claude Code 프로젝트 설정(`.claude/`)을 OpenAI Codex 호환 스킬 형식으로 마이그레이션합니다.

**변환 대상:**
- `.claude/commands/*.md` → Codex 스킬 디렉토리
- `.claude/skills/*.md` → Codex 스킬 디렉토리 (대용량 파일은 progressive disclosure 적용)
- `P1-P4_rules.md` → code-review 스킬 references
- `CLAUDE.md` / `AGENTS.md` → 호환성 분석
- 설치된 Claude 플러그인 에셋 → 네임스페이스 접두사가 붙은 Codex 스킬

**사용법:**

```bash
# 1. 미리보기 (dry-run)
python ~/.codex/skills/claude-to-codex-migrator/scripts/migrate.py . --dry-run

# 2. 마이그레이션 실행
python ~/.codex/skills/claude-to-codex-migrator/scripts/migrate.py .
```

**주요 옵션:**
- `--dry-run` — 파일 생성 없이 미리보기
- `--output-dir PATH` — 사용자 지정 출력 디렉토리
- `--force` — 기존 파일 덮어쓰기
- `--plugins NAME [...]` — 특정 플러그인만 변환
- `--format json` — JSON 출력

**플러그인 설정:**

설치된 Claude 플러그인을 포함하려면 `.claude/codex-migration.json` 파일을 생성합니다:

```json
{"plugins": ["platform-dev-team-common", "sdd-helper"]}
```

자세한 포맷 매핑은 `skills/claude-to-codex-migrator/references/format-mapping.md`를 참고하세요.

## 에이전트 (Agents)

추가 예정

## 빠른 시작

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add orchwang/orchwang-claude-marketplace

# 2. 플러그인 설치
/plugin install orchwang-general@orchwang-marketplace
```

## 라이선스

MIT
