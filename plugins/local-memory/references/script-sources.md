# Script Sources Reference

local-memory 플러그인이 "스크립트"로 식별하여 외부기억에 동기화하는 파일 종류·위치·저장 규칙을 정의한다. `sync-scripts` skill과 `repo-memory` 에이전트는 본 문서의 규칙만 사용한다.

> 본 문서는 `scope=scripts` 전용 레퍼런스이다. spec 문서 동기화는 별도 흐름(`/sync-specs`, `scope=specs`)을 사용한다.

## 카테고리 정의

| 카테고리 | 글롭 | 저장 디렉토리 | 코드 펜스 | 비고 |
|---------|-----|-------------|---------|------|
| bash | `scripts/**/*.sh`, `bin/**/*.sh`, 실행권한이 켜진 `*.sh` | `scripts/bash/` | ` ```bash ` | shebang은 검사하지 않음. 확장자·경로 우선 |
| makefile | `Makefile`, `*/Makefile` (1-depth), `*.mk` | `scripts/makefile/` | ` ```makefile ` | 본문 그대로 보존 |
| django-command | `**/management/commands/*.py` (제외: `__init__.py`) | `scripts/django-command/{app}/` | ` ```python ` | `{app}` = `management/`의 상위 두 디렉토리 이름 |

## 제외 규칙

- 파일명 `__init__.py`는 모든 카테고리에서 제외
- `node_modules/`, `.git/`, `.venv/`, `dist/`, `build/` 하위는 모든 카테고리에서 제외
- 루트-레벨 평면 카테고리 폴더(`django-commands/`, `bash/` 등)는 인식 대상이 아니다 — 반드시 위 표의 글롭과 정확히 일치해야 한다. 레거시 평면 트리는 `docs/migrations/datamaker-docs-django-commands.md`를 참고하여 수동 마이그레이션한다

## 파일명 인코딩 규칙

원본 repo 내 상대경로를 카테고리 디렉토리 하위의 단일 `.md` 파일명으로 변환할 때 아래 규칙을 따른다.

- 일반 규칙: 상대경로의 `/`를 `__`로 치환하고 확장자를 `.md`로 변경
  - 예: `scripts/deploy/run.sh` → `scripts/bash/scripts__deploy__run.md`
  - 예: `Makefile` → `scripts/makefile/Makefile.md`
- django-command 예외: `{app}` 디렉토리를 분리하여 보존하고, 파일명은 명령 이름만 사용
  - 예: `apps/celery/management/commands/verify_beat_schedules.py` → `scripts/django-command/celery/verify_beat_schedules.md`
- 파일명이 OS 한계(예: 255자)를 넘는 경우는 본 작업 범위 외(향후 슬러그 해시 fallback 고려)

## 자연어 의도 사전 (intent dictionary)

사용자의 자연어 요청을 `scope` 값으로 라우팅하기 위한 매핑. 에이전트는 의도가 모호할 때 본 표를 참조하고, 두 영역 표현이 혼재하면 사용자에게 명시 확인한다.

| 사용자 표현 | scope |
|------------|-------|
| "django command", "manage.py", "management command", "장고 명령" | scripts |
| "bash 스크립트", "shell 스크립트", "*.sh", "쉘 스크립트" | scripts |
| "Makefile", "make 타겟", "메이크파일" | scripts |
| "requirements", "specs", "plans", "스펙 문서", "요구사항", "기획" | specs |
| "메모", "아이디어", "idea" | (별도 `save-idea`) |

> 두 영역 표현이 한 문장에 동시에 등장하면(예: "스펙과 스크립트 같이 저장해줘") 에이전트는 `AskUserQuestion`으로 영역을 분리하여 묻는다. 임의로 `scope=all` 라우팅하지 않는다.

## frontmatter 형식

각 스크립트 노트는 아래 frontmatter를 포함한다.

```yaml
---
source_path: {repo 내 상대경로}
script_type: bash | makefile | django-command
repo: {repo-name}
synced_at: {YYYY-MM-DDThh:mm:ss±zz:zz}
tags:
  - repo/{repo-name}
  - scripts
  - {script_type}
---
```

본문은 `# {source_path}` 제목 다음에 카테고리별 코드 펜스로 원본 그대로 감싼다.

## 향후 확장 후보

본 작업 범위에 포함되지 않으며 향후 카테고리 추가 시 본 표만 확장하면 합류 가능.

| 후보 카테고리 | 글롭 후보 | 코드 펜스 |
|-------------|---------|---------|
| justfile | `justfile`, `*/justfile` | ` ```just ` |
| npm scripts | `package.json` (scripts 필드 추출) | ` ```json ` 또는 ` ```bash ` |
| github-actions | `.github/workflows/*.yml` | ` ```yaml ` |
