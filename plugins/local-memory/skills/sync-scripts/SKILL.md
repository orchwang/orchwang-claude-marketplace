---
name: sync-scripts
description: 저장소의 스크립트(bash / makefile / django-command)를 외부기억의 scripts/ 트리에 동기화한다. Use when the user wants to sync scripts, or mentions "sync scripts", "스크립트 동기화", "django command 저장", "manage.py 명령 저장", "bash 스크립트 저장", "Makefile 저장", "shell 스크립트 저장".
---

# sync-scripts

저장소의 스크립트를 선택된 백엔드(obsidian / filesystem / git)의 `scripts/` 트리에 동기화하는 skill.

> 카테고리 인식 규칙과 자연어 의도 매핑은 `references/script-sources.md`를, 백엔드별 명령은 `references/backend-operations.md`를 참조한다.
>
> spec 문서 동기화는 `/sync-specs`를 사용하세요 — 두 영역은 별도 skill로 분리되어 있습니다.

## Input

`/sync-scripts [<glob-or-path>] [--category bash|makefile|django-command|all]`

- `/sync-scripts` — 모든 카테고리·모든 매칭 파일 동기화
- `/sync-scripts scripts/deploy` — 경로 한정
- `/sync-scripts --category bash` — 카테고리 한정
- `/sync-scripts apps/celery --category django-command` — 경로 + 카테고리

## Process

### Step 1: 컨텍스트 확인

`repo-memory` 에이전트를 `scope=scripts`로 호출하여 Pre-flight check 및 컨텍스트를 수신한다.

수신 인자:

- `backend`: `.claude/local-memory.json`의 `backend`
- 백엔드별 저장 대상: obsidian 분기 본문 안에서만 등장하는 `vault-name` / filesystem·git 분기의 `basePath`
- `directory`: 하위 디렉토리 이름
- `repo-name`: git remote 또는 디렉토리명에서 추출

에이전트는 `scope=scripts` 컨텍스트에서 다음을 보장:

- `{directory}/{repo-name}/scripts/<카테고리>/` 디렉토리 lazy-create
- 인덱스 노트(`{repo-name}.md`)의 비파괴 병합 — `## Scripts` 섹션이 없으면 한 번만 append

### Step 2: 인자 파싱

1. 위치 인자에서 `<glob-or-path>` 추출 (선택)
2. `--category` 옵션 파싱: `bash`, `makefile`, `django-command`, `all` (선택, 기본 `all`)
3. 카테고리 값이 유효하지 않으면 "[scripts] 지원 카테고리: bash, makefile, django-command, all" 안내 후 중단

### Step 3: 후보 파일 수집

`references/script-sources.md`의 글롭/제외 규칙대로 후보를 수집한다.

```bash
# bash
find . \( -path "./scripts/*" -o -path "./bin/*" \) -name "*.sh" -type f
find . -name "*.sh" -perm +111 -type f   # 실행권한이 켜진 *.sh (추가)

# makefile
find . -maxdepth 2 -type f \( -name "Makefile" -o -name "*.mk" \)

# django-command (제외: __init__.py)
find . -path "*/management/commands/*.py" -type f ! -name "__init__.py"
```

위 결과에서 `node_modules/`, `.git/`, `.venv/`, `dist/`, `build/` 하위는 제외한다.

`<glob-or-path>` 인자가 있으면 그 범위로 한정한다. `--category` 인자가 `all`이 아니면 해당 카테고리만 수집한다.

후보가 0건이면:

- "[scripts] 동기화할 스크립트가 없습니다. `references/script-sources.md`의 규칙과 인자 범위를 확인하세요."로 보고 후 중단.

### Step 4: 파일별 frontmatter + 코드 펜스 합성

각 후보 파일에 대해:

1. **카테고리 결정**: 경로·글롭으로 `bash` / `makefile` / `django-command` 중 하나로 분류
2. **저장 경로 결정**:
   - 일반: `{directory}/{repo-name}/scripts/{카테고리}/{인코딩 파일명}.md`
   - django-command 예외: `{directory}/{repo-name}/scripts/django-command/{app}/{command}.md`
     - `{app}`: 원본 경로에서 `management/`의 상위 두 디렉토리 중 직속 디렉토리 이름
     - `{command}`: 원본 `.py` 파일명에서 `.py` 제거
   - 일반 인코딩: 상대경로의 `/`를 `__`로 치환하고 `.md`로 확장
3. **frontmatter 합성**:

   ```yaml
   ---
   source_path: {repo 내 상대경로}
   script_type: bash | makefile | django-command
   repo: {repo-name}
   synced_at: {ISO-8601}
   tags:
     - repo/{repo-name}
     - scripts
     - {script_type}
   ---
   ```

4. **본문 합성**:

   ```markdown
   # {source_path}

   ​```{펜스 언어}
   {원본 그대로}
   ​```
   ```

   펜스 언어: `bash` / `makefile` / `python`

### Step 5: 백엔드별 CREATE

`references/backend-operations.md`의 CREATE 연산을 사용한다.

#### backend = obsidian

```bash
obsidian vault="{vault-name}" create name="{인코딩 파일명}" path="{directory}/{repo-name}/scripts/{카테고리}[/{app}]" content="{frontmatter + 본문}" overwrite silent
```

#### backend = filesystem

```bash
mkdir -p "{basePath}/{directory}/{repo-name}/scripts/{카테고리}[/{app}]"
cat > "{basePath}/{directory}/{repo-name}/scripts/{카테고리}[/{app}]/{인코딩 파일명}.md" << 'CONTENT_EOF'
{frontmatter + 본문}
CONTENT_EOF
```

#### backend = git

filesystem과 동일하게 파일을 쓰되, **모든 파일 쓰기가 완료된 후** 한 번만 커밋+push:

```bash
cd "{basePath}" && git add -A && git commit -m "local-memory: sync scripts from {repo-name}" && git push {gitRemote}
```

### Step 6: 결과 보고

모든 출력 메시지는 `[scripts]` 접두 라벨을 사용한다 (한 메시지에서 specs 영역과 혼합 금지).

```
[scripts] 스크립트 동기화 완료: {backend별 저장 위치}

동기화된 카테고리:
  - bash: N개
  - makefile: M개
  - django-command: L개

총 {N+M+L}개 파일, 실패 {F}개

실패 항목:
  - {실패 파일 경로}: {원인}
```

## Content 전달 시 주의사항

- obsidian 백엔드: `obsidian create`의 `content` 값에 줄바꿈은 `\n`, 탭은 `\t`로 이스케이프한다
- 큰따옴표가 포함된 내용은 이스케이프 처리한다
- frontmatter의 `---` 구분자가 content에 포함되어야 한다
- 원본 스크립트 본문은 임의 변형(formatter, lint)하지 않고 그대로 보존한다
- 파일 읽기 실패(권한 등)는 해당 파일만 스킵하고 결과 보고의 실패 목록에 포함한다

## 결과 활용

저장된 스크립트는 `repo-memory(scope=scripts)`로 검색할 수 있다. 예:

```bash
# obsidian
obsidian vault="{vault-name}" search query="path:{directory}/{repo-name}/scripts" limit=50

# filesystem / git
find "{basePath}/{directory}/{repo-name}/scripts" -name "*.md" -type f
```

> 통합 검색이 필요할 때는 `scope=all` 호출을 사용한다 — 단, 출력은 `[specs]`와 `[scripts]`로 분리되어 보고된다.
