# Migration: datamaker-docs `django-commands/` → `scripts/django-command/`

> Status: 가이드 (사용자 수동 실행)
> Audience: `/Users/jongtaek.hwang/Projects/datamaker-docs`를 local-memory 외부기억으로 사용 중인 사용자
> Plugin: local-memory v2.1.0 이상

## 배경

local-memory v2.1.0은 저장소 내 스크립트(bash · makefile · django command)를 외부기억의 `{repo-name}/scripts/<카테고리>/` 트리에 동기화하는 기능을 도입했다.

datamaker-docs에는 이미 v2.0.0 이전부터 루트 평면 트리로 `django-commands/<도메인>/<command>.py` 구조의 데이터가 적재되어 있다. 이 구조는 v2.1.0의 카테고리 규칙(`{repo-name}/scripts/django-command/{app}/`)과 일치하지 않으므로 재분류 마이그레이션이 필요하다.

본 마이그레이션은 **사용자 수동 작업**이며, local-memory 플러그인 코드는 어떤 자동 변환도 수행하지 않는다. 데이터 안전성을 위해 모든 변환은 사용자가 직접 가이드를 따라 실행한다.

## 영향 범위

- 소스: `/Users/jongtaek.hwang/Projects/datamaker-docs/django-commands/<도메인>/*.py`
- 대상: `/Users/jongtaek.hwang/Projects/datamaker-docs/{directory}/synapse-backend/scripts/django-command/<도메인>/<command>.md`
- 관찰된 도메인(2026-05-13 기준): `celery`, `import`, `export`, `statistics`, `plugin`, `assignment`, `file-operations`, `data-files`, `format-conversion`, `project-specific`, `rapa-project`, `setup`, `utility`
- `{directory}` 값은 `.claude/local-memory.json`의 `directory`. 기본 적재 시 `claude-memory`

> 본 마이그레이션은 FR-9(Plugin Update Migration)의 자동 lazy-migration 대상이 **아니다**. v2.1.0 업그레이드 자체는 위 데이터를 건드리지 않는다.

## 사전 검사

1. `local-memory` 플러그인이 v2.1.0 이상인지 확인
   ```bash
   cat plugins/local-memory/plugin.json | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
   ```
2. `datamaker-docs` repo의 백엔드 설정 확인
   ```bash
   cat /Users/jongtaek.hwang/Projects/datamaker-docs/.claude/local-memory.json 2>/dev/null || echo "MISSING"
   ```
   - `backend`가 `git` 또는 `filesystem`인지 확인. obsidian인 경우 본 가이드의 명령은 그대로 적용되지 않으며, obsidian vault 안에서 동등 절차를 수행해야 한다
3. `synapse-backend` 외부기억 트리 초기화
   ```bash
   # synapse-backend repo에서 1회 실행:
   # /check-settings   →  설정 확인
   # /sync-scripts --category django-command   →  scripts/django-command/ 트리 생성
   ```

## 변환 절차

도메인별로 동일 절차를 반복한다. 본 예시는 `celery` 도메인 기준.

### Step 1: 대상 디렉토리 준비

```bash
BASE=/Users/jongtaek.hwang/Projects/datamaker-docs
DIRECTORY=$(python3 -c "import json; print(json.load(open('$BASE/.claude/local-memory.json'))['directory'])" 2>/dev/null || echo claude-memory)
DOMAIN=celery
mkdir -p "$BASE/$DIRECTORY/synapse-backend/scripts/django-command/$DOMAIN"
```

### Step 2: 각 `.py` 파일을 `.md`로 변환

```bash
SRC_DIR="$BASE/django-commands/$DOMAIN"
DST_DIR="$BASE/$DIRECTORY/synapse-backend/scripts/django-command/$DOMAIN"

for src in "$SRC_DIR"/*.py; do
  [ -f "$src" ] || continue
  name=$(basename "$src" .py)
  [ "$name" = "__init__" ] && continue
  dst="$DST_DIR/$name.md"

  {
    echo "---"
    echo "source_path: apps/${DOMAIN}/management/commands/${name}.py"
    echo "script_type: django-command"
    echo "repo: synapse-backend"
    echo "synced_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "tags:"
    echo "  - repo/synapse-backend"
    echo "  - scripts"
    echo "  - django-command"
    echo "---"
    echo
    echo "# apps/${DOMAIN}/management/commands/${name}.py"
    echo
    echo '```python'
    cat "$src"
    echo '```'
  } > "$dst"

  echo "converted: $src → $dst"
done
```

> `source_path`는 원본 repo(`synapse-backend`) 안에서 해당 command가 있던 정확한 경로를 사용한다. 도메인 폴더가 `apps/{domain}/`에 직접 매핑되지 않는 경우 실제 경로로 보정한다.

### Step 3: 도메인 반복

위 두 스텝을 모든 도메인에 대해 반복한다. 본 가이드 작성 시점의 도메인 목록은 다음과 같다(현장에서 실측 후 갱신):

```bash
for DOMAIN in celery import export statistics plugin assignment file-operations data-files format-conversion project-specific rapa-project setup utility; do
  mkdir -p "$BASE/$DIRECTORY/synapse-backend/scripts/django-command/$DOMAIN"
  # Step 2의 변환 루프 반복
done
```

### Step 4: git 백엔드 커밋

git 백엔드를 사용 중이면 변환을 모두 마친 후 단일 커밋으로 묶는다:

```bash
cd "$BASE"
git add -A
git status -s | head -30   # 변경 분량 확인
git commit -m "local-memory: migrate django-commands to scripts/django-command"
git push origin
```

## 검증

1. 변환된 파일 수가 원본 `.py` 수(제외: `__init__.py`)와 일치하는지 확인
   ```bash
   SRC_COUNT=$(find "$BASE/django-commands" -name "*.py" ! -name "__init__.py" -type f | wc -l)
   DST_COUNT=$(find "$BASE/$DIRECTORY/synapse-backend/scripts/django-command" -name "*.md" -type f | wc -l)
   echo "src=$SRC_COUNT dst=$DST_COUNT"   # 일치해야 함
   ```
2. spot check 3건: 무작위로 3개 도메인의 1개씩 골라 frontmatter 5개 필드(`source_path`, `script_type`, `repo`, `synced_at`, `tags`)와 `​```python` 펜스, 본문이 원본과 일치하는지 확인
3. `synapse-backend` repo에서 `/check-settings` 실행 — "마이그레이션 감사" 절에서 `## Scripts` 섹션이 OK, 레거시 평면 트리가 여전히 INFO로 보고되는지 확인 (Step 5 정리 전까지)

## 정리: 레거시 트리 제거

검증을 모두 마친 후에만 원본 `django-commands/` 트리를 제거한다.

```bash
cd "$BASE"
git rm -r django-commands
git status -s
git commit -m "local-memory: remove legacy django-commands tree (migrated to scripts/django-command)"
git push origin
```

> 검증 완료 전에 원본을 삭제하지 마세요. 변환 실수를 발견하면 git history에서 복구할 수 있도록 두 단계로 분리합니다.

## 자동 변환 미제공 사유

- 도메인 폴더와 원본 repo의 `apps/<domain>/management/commands/` 매핑이 1:1이 아닐 수 있어 `source_path` 자동 추론이 부정확할 위험
- 일부 도메인에 비표준 파일(README, helper 등)이 섞여 있을 가능성
- 데이터 손실 위험을 최소화하기 위해 단계별 검증 후 사용자 명시 승인으로 진행

향후 사용자 피드백을 바탕으로 자동 변환 옵션을 별도 skill 또는 `--migrate-from <path>` 인자로 도입하는 안을 고려할 수 있다 (현재 범위 외).
