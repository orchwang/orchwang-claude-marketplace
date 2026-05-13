# Plans: Sync scripts for local-memory plugin

> Created: 2026-05-13
> Updated: 2026-05-13 (Step 1–10 구현 완료)
> Status: Implemented (라이브 검증 대기)
> Requirements: [requirements.md](./requirements.md)
> Specs: [specs.md](./specs.md)

## Overview

본 작업은 `local-memory` 플러그인을 확장하여 (1) 저장소의 스크립트(bash / makefile / django command)를 specs와 동등한 1급 시민으로 동기화하고, (2) `specs` / `scripts` 영역을 어휘·skill·scope 차원에서 격리하며, (3) 표면 텍스트의 obsidian 우선 어조를 백엔드 중립으로 정리한다.

구현은 10단계로 진행한다. 의존도 순서대로 **레퍼런스 → 에이전트 → 명령어 → 신규 skill → 기존 skill 격리 → 패키지/문서 → 마이그레이션 가이드(레거시) → 업그레이드 동선(기존 사용자)**의 흐름을 따른다. 모든 단계의 변경은 마크다운 파일 중심이며 실행 코드 변경은 없다(플러그인은 마크다운 spec 기반 동작).

### Open Questions 결정 (Specs 미해결 항목 처리)

`specs.md`의 Open Questions에 대한 본 plan 기준 결정:

| Open Question | 결정 |
|--------------|------|
| `<relpath-encoded>` 충돌 규칙 충분성 | 채택. 경로명이 OS 파일명 제한(예: 255자)을 넘는 경우만 슬러그 해시 fallback. 본 작업에서는 fallback 미구현, 향후 이슈로 분리 |
| Django command 파일명 형식 | `scripts/django-command/{app}/<command>.md` — app은 디렉토리, command가 파일명. datamaker-docs 도메인 폴더 관례와 정합 |
| `--since <ref>` 변경분 기반 동기화 | 본 범위 외. 향후 후속 작업 |
| 레거시 마이그레이션 자동 변환 스크립트 | 미제공. 가이드 문서만 작성하고 사용자 수동 변환 |
| 기존 사용자 데이터(v2.0.0) 자동 마이그레이션 정책 | 비파괴 lazy-migration 채택. 업그레이드 행위 자체는 데이터를 건드리지 않고, `/sync-scripts` 첫 호출 시 인덱스 노트에 `## Scripts` 섹션을 비파괴 append (FR-9) |

## Prerequisites

- 본 repo(`orchwang-claude-marketplace`)에서 작업
- `plugins/local-memory/`가 v2.0.0(abstraction-for-local-memory-plugin 완료 상태)인지 확인
- `references/backend-operations.md`, `agents/repo-memory/AGENT.md`, `commands/check-settings.md`, `skills/sync-specs/SKILL.md`, `skills/save-idea/SKILL.md` 모두 존재 확인
- 작성·편집 시 한국어, 2-space YAML 들여쓰기, kebab-case 파일명(`AGENTS.md` 규칙) 준수
- 외부 의존성 추가 없음

## Implementation Steps

### Step 1: `references/script-sources.md` 생성

- **Goal**: 스크립트 카테고리 인식 규칙과 자연어 의도 사전을 단일 레퍼런스로 둔다. 모든 skill/agent가 본 문서를 참조한다.
- **Specs Reference**: specs.md "Script Source Reference", "Instruction isolation (FR-7) #3 자연어 의도 사전"
- **Files**:
  - `plugins/local-memory/references/script-sources.md` — Create
- **Details**:
  - 섹션 구성: (1) 카테고리 정의 표, (2) 글롭/제외 규칙, (3) 파일명 인코딩 규칙, (4) 자연어 의도 사전 표, (5) 향후 확장 후보
  - 카테고리 정의 표
    | 카테고리 | 글롭 | 저장 디렉토리 | 코드 펜스 | 비고 |
    |---------|-----|-------------|---------|------|
    | bash | `scripts/**/*.sh`, `bin/**/*.sh`, 실행권한 `*.sh` | `scripts/bash/` | ` ```bash ` | shebang 무관, 확장자 우선 |
    | makefile | `Makefile`, `*/Makefile`(1-depth), `*.mk` | `scripts/makefile/` | ` ```makefile ` | 본문 그대로 |
    | django-command | `**/management/commands/*.py`(제외: `__init__.py`) | `scripts/django-command/{app}/` | ` ```python ` | `{app}` = `management/`의 상위 두 디렉토리 이름 |
  - 파일명 인코딩 규칙: 원본 상대경로의 `/`를 `__`로 치환. django-command는 `{app}` 디렉토리 분리 보존.
  - 루트 레벨 평면 트리(`django-commands/`, `bash/` 등) 인식 제외 명시
  - 자연어 의도 사전 표 (FR-7 #3):
    | 사용자 표현 | scope |
    |-----------|-------|
    | "django command", "manage.py", "management command", "장고 명령" | scripts |
    | "bash 스크립트", "shell 스크립트", "*.sh", "쉘 스크립트" | scripts |
    | "Makefile", "make 타겟", "메이크파일" | scripts |
    | "requirements", "specs", "plans", "스펙 문서", "요구사항", "기획" | specs |
    | "메모", "아이디어", "idea" | (별도 save-idea) |
  - 향후 확장 후보: Justfile(`justfile`), npm scripts(`package.json` scripts), GitHub Actions YAML
- **Validation**:
  - `grep -E "django-command|bash|makefile" plugins/local-memory/references/script-sources.md` 가 정의 표·인코딩 규칙·의도 사전 모두에 해당하는 라인을 반환
  - 본문에 "Obsidian이 없는", "기본값: obsidian" 등 위계 표현이 없음
- **Complexity**: Simple

### Step 2: `references/backend-operations.md`에 scope 차원 추가

- **Goal**: SEARCH 연산에 `scope: specs | scripts | all` 분기를 추가하여 검색 경로가 영역별로 한정되도록 한다.
- **Specs Reference**: specs.md "repo-memory 에이전트 계약 확장" SEARCH 표
- **Files**:
  - `plugins/local-memory/references/backend-operations.md` — Modify
- **Details**:
  - 기존 SEARCH 섹션 아래에 "Scope-aware SEARCH" 서브섹션 신설:
    ```markdown
    ### SEARCH (scope 한정)
    | scope | obsidian | filesystem / git |
    |-------|----------|-----------------|
    | specs | obsidian vault="{vault}" search query="path:{directory}/{repo}/specs" limit={N} | find "{basePath}/{directory}/{repo}/specs" -name "*.md" -type f |
    | scripts | obsidian vault="{vault}" search query="path:{directory}/{repo}/scripts" limit={N} | find "{basePath}/{directory}/{repo}/scripts" -name "*.md" -type f |
    | all | obsidian vault="{vault}" search query="path:{directory}/{repo}" limit={N} | find "{basePath}/{directory}/{repo}" -name "*.md" -type f |
    ```
  - 기존 단일 SEARCH 표는 유지하되 "기본(scope 미지정 시 동작)으로는 path가 직접 지정된 경로를 검색한다"는 한 줄 주석 추가
  - 링크 형식 절(파일 맨 끝)에 `scripts/`도 적용됨을 한 줄 추가
- **Validation**:
  - `backend-operations.md`에 `scope` 단어가 최소 3회 등장
  - SEARCH 섹션이 scope-aware 표를 포함
- **Complexity**: Simple

### Step 3: `agents/repo-memory/AGENT.md` 업데이트 (scope + scripts 초기화 + 라벨 + FR-8 중립화)

- **Goal**: 에이전트가 `scope` 인자를 받아 검색·초기화를 분기하고, scripts 폴더 트리를 초기화하며, 출력 메시지에 `[specs]`/`[scripts]` 라벨을 사용하고, 표면 텍스트를 백엔드 중립으로 정리한다.
- **Specs Reference**: specs.md "repo-memory 에이전트 계약 확장", "Instruction isolation (FR-7)", "Backend-neutral framing (FR-8)" §AGENT.md
- **Files**:
  - `plugins/local-memory/agents/repo-memory/AGENT.md` — Modify
- **Details**:
  - frontmatter `description`을 중립으로: `"… 선택된 백엔드(obsidian / filesystem / git)에 관리하는 에이전트. sync-specs, sync-scripts, save-idea skill 실행 시 사전 검사 및 repo 컨텍스트를 제공한다."`
  - 본문 첫 단락의 "Obsidian vault, 로컬 파일시스템, 또는 git 저장소" 문구는 유지 가능하나, 우선순위·"기본값" 강조 제거
  - **새 절: "Skill 호출 계약 (scope 인자)"** 추가
    - 입력 인자 명세: `scope: "specs" | "scripts" | "all"` (필수). 미지정 시 사용자에게 `AskUserQuestion`으로 명시 확인 후 진행
    - 호출 매핑: `sync-specs` → `scope=specs`, `sync-scripts` → `scope=scripts`, 통합 검색 → `scope=all`
  - `## Pre-flight Check` 결과 출력 메시지에 `[specs]` / `[scripts]` 라벨 접두 사용 규칙 추가 (실제 검사 명령은 동일)
  - 섹션 헤더 `## Vault 설정 읽기` → `## 백엔드 설정 읽기`
  - `## 백엔드 설정 읽기` 본문에서 "기본값: `obsidian`" 같은 라인은 별도 Note(`> Note: …`) 한 줄로 분리하고 표/본문 강조에서 제외
  - `vault-name` 변수는 obsidian 분기 본문 안에서만 사용. 다른 백엔드 절에서는 등장 금지
  - `## 저장소 폴더 구조 초기화` 절 확장:
    - 인덱스 노트 템플릿에 `## Scripts` 섹션을 `## Specs` 다음(또는 `## Ideas` 직전)에 추가
    - obsidian 분기: `![[{directory}/{repo-name}/scripts]]`
    - filesystem/git 분기: `- [scripts](./{repo-name}/scripts/)`
    - `scope=scripts` 또는 `scope=all` 호출 시 필요한 카테고리 디렉토리(`scripts/bash`, `scripts/makefile`, `scripts/django-command`)도 생성하도록 절차 추가
  - **새 절: "인덱스 노트 비파괴 병합"(FR-9)** 추가:
    - 입력: scope, repo-name, 백엔드 메타
    - 절차: EXISTS → 미존재면 신규 템플릿 생성 / 존재면 READ → `## Scripts` 정확 일치 헤딩 탐색 → 부재 시 `## Ideas` 직전(또는 본문 끝)에 마크다운 블록 삽입 → CREATE(overwrite)로 다시 쓰기
    - 헤딩 검출은 라인 단위 정확 일치(`^## Scripts\s*$`). 본문 내 인용·코드블록 안 헤딩은 무시(보수적으로 헤딩만 매칭)
    - 사용자가 직접 추가한 다른 섹션은 전부 보존
    - 두 번째 호출부터는 헤딩 존재 검출에서 no-op로 종료
  - `## Skill 조율` 절에 `sync-scripts` 항목을 `sync-specs` 다음에 추가 — 한 줄 설명만, cross-detail 금지
- **Validation**:
  - `grep -n "scope" AGENT.md` 가 새 섹션·계약·예시에서 등장
  - `grep -n "Vault 설정 읽기" AGENT.md` 가 0건
  - 인덱스 템플릿에 `## Scripts` 가 포함됨
- **Complexity**: Medium

### Step 4: `commands/check-settings.md` 업데이트 (scripts 헬스체크 + Django 휴리스틱 + 라벨 분리 + FR-8 중립화)

- **Goal**: `/check-settings`가 scripts 트리 쓰기 가능 여부를 별도로 검증하고, Django 휴리스틱을 정보성으로 보고하며, 출력에 `[specs]`/`[scripts]` 라벨을 사용한다.
- **Specs Reference**: specs.md "/check-settings 확장", "Instruction isolation (FR-7) #5 Pre-flight check 메시지 분리", "Backend-neutral framing (FR-8) §check-settings.md"
- **Files**:
  - `plugins/local-memory/commands/check-settings.md` — Modify
- **Details**:
  - Step 1 환경 검사에 **§1.5 Django 휴리스틱(정보성)** 신설:
    - `test -f manage.py` 또는 `find . -maxdepth 3 -name manage.py`
    - OK/MISSING이 아닌 INFO 상태(에러 아님). MISSING 시 "Django 프로젝트가 아닙니다. `[scripts]` django-command 카테고리는 생성되지 않습니다." 정보성 메시지
  - Step 5 연결 테스트에 **scripts 헬스체크** 추가:
    - obsidian: `obsidian vault="{vault-name}" create name=".healthcheck" path="{directory}/{repo-name}/scripts" content="ok" overwrite silent` → 이어서 read/delete 동등 동작
    - filesystem/git: `mkdir -p "{basePath}/{directory}/{repo-name}/scripts" && echo ok > .../scripts/.healthcheck.md && cat ... && rm ...`
    - 결과 메시지는 `[scripts]` 라벨 접두 사용
    - 기존 specs 헬스체크가 없는 경우 함께 `[specs]` 라벨 헬스체크 흐름도 동일 패턴으로 추가 (영역별 메시지 분리 원칙 충족)
  - FR-8 중립화:
    - `### 2.3 vault (obsidian 백엔드만)`, `### 2.4 basePath (filesystem / git 백엔드만)` 같은 단서 절은 유지
    - "스토리지 백엔드를 선택해주세요: obsidian / filesystem / git" 프롬프트는 유지하되, **기본값 무음 적용 금지** — backend MISSING이면 무조건 사용자에게 묻는다(기본값으로 자동 채우지 않음). 본 절차를 명시
    - "obsidian 백엔드 사용 시" 같은 절대적 권장 어휘 사용 금지
  - **새 절: "마이그레이션 감사"(FR-9)** 추가 — Step 3 결과 출력 다음:
    - 항목별 OK/MISSING/INFO 상태 표 출력
      - 인덱스 노트 존재 여부 (EXISTS)
      - 인덱스 노트의 `## Scripts` 섹션 존재 여부 (READ + 헤딩 검출)
      - `{directory}/{repo}/scripts/` 디렉토리 존재 여부
      - filesystem/git 백엔드 한정: `{basePath}/django-commands/` 같은 루트 평면 트리 존재 여부 (INFO만, 에러 아님)
    - 각 MISSING 항목 옆에 보강 명령 안내 (예: `/sync-scripts`)
    - 본 절은 정보성. 실제 변경은 사용자가 안내된 명령을 실행할 때만 발생
- **Validation**:
  - `grep -n "manage.py" check-settings.md` 가 §1.5에 등장
  - `grep -nE "\[scripts\]|\[specs\]" check-settings.md` 가 결과 출력 예시에서 등장
  - "기본값 obsidian" 자동 적용 문구가 없음
- **Complexity**: Medium

### Step 5: `skills/sync-scripts/SKILL.md` 신규 작성

- **Goal**: `sync-specs`와 대칭되는 신규 skill 작성. `scope=scripts`로 `repo-memory`를 호출하고, 카테고리별 파일 수집·frontmatter·CREATE 명령을 백엔드별로 실행한다. FR-7 격리 규칙을 처음부터 준수.
- **Specs Reference**: specs.md "sync-scripts Skill 흐름", "Instruction isolation (FR-7) #1 Skill 파일 분리·자기완결성", FR-2 acceptance criteria
- **Files**:
  - `plugins/local-memory/skills/sync-scripts/SKILL.md` — Create
- **Details**:
  - frontmatter:
    - `name: sync-scripts`
    - `description`: 트리거 단어 — "sync scripts", "스크립트 동기화", "django command 저장", "manage.py 명령 저장", "bash 스크립트 저장", "Makefile 저장". specs 영역 트리거 단어 사용 금지.
  - 본문 절 순서:
    1. Input — `/sync-scripts [<glob-or-path>] [--category bash|makefile|django-command|all]`
    2. Process Step 1: 컨텍스트 확인 — `repo-memory(scope=scripts)` 호출. 결과 인자(backend, basePath/vault, directory, repo-name) 수신. specs 영역 어휘 사용 금지.
    3. Process Step 2: 인자 파싱 — glob/path/category 분리. 미지정 시 모든 카테고리.
    4. Process Step 3: 후보 파일 수집 — `references/script-sources.md`의 글롭/제외 규칙대로 수집. 결과 0건이면 "[scripts] 동기화할 스크립트가 없습니다. references/script-sources.md의 규칙을 확인하세요."
    5. Process Step 4: 파일별 frontmatter + 코드 펜스 합성
       - frontmatter:
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
       - 본문:
         ```markdown
         # {source_path}

         ​```{펜스 언어}
         {원본 그대로}
         ​```
         ```
    6. Process Step 5: 백엔드별 CREATE
       - obsidian / filesystem / git 분기는 `references/backend-operations.md`를 참조하여 동일 패턴 적용
       - 저장 경로: `{directory}/{repo-name}/scripts/{카테고리}/{인코딩 파일명}.md`
       - django-command는 `{카테고리}/{app}/{command}.md`로 한 단계 더 분리
    7. Process Step 6: git 백엔드 단일 커밋+push — 모든 파일 작성 후 한 번만 `git add -A && git commit -m "local-memory: sync scripts from {repo-name}" && git push {gitRemote}`
    8. Process Step 7: 결과 보고 — 카테고리별 개수, 실패 항목, 모든 메시지에 `[scripts]` 접두
  - 본문 끝에 한 줄 경계만 두기: `> spec 문서 동기화는 /sync-specs를 사용하세요.` (cross-detail 금지)
  - frontmatter description에 "vault", "obsidian" 단어를 1순위로 배치하지 않음 (FR-8)
- **Validation**:
  - 파일이 존재, `description`에 specs 트리거 단어(`requirements`, `plans`, `스펙 문서`) 부재
  - 모든 결과 메시지 예시에 `[scripts]` 접두
  - `scope=scripts` 인자가 `repo-memory` 호출에 명시
- **Complexity**: Complex

### Step 6: `skills/sync-specs/SKILL.md` 및 `skills/save-idea/SKILL.md` 격리·중립화 정리

- **Goal**: 기존 두 skill에서 scripts 트리거 단어 유입을 사전 차단하고, `scope=specs` / `scope=ideas`(별개)를 호출 인자에 명시하며, frontmatter description과 본문을 백엔드 중립으로 정리한다.
- **Specs Reference**: specs.md "Instruction isolation (FR-7) #1, #2", "Backend-neutral framing (FR-8) §sync-specs/save-idea"
- **Files**:
  - `plugins/local-memory/skills/sync-specs/SKILL.md` — Modify
  - `plugins/local-memory/skills/save-idea/SKILL.md` — Modify
- **Details**:
  - `sync-specs/SKILL.md`:
    - 첫 단락 "specs 문서를 Obsidian vault 또는 로컬 파일시스템에 동기화하는 skill" → "specs 문서(requirements / specs / plans)를 선택된 백엔드(obsidian / filesystem / git)에 동기화하는 skill"
    - Process Step 1에서 `repo-memory` 호출을 `repo-memory(scope=specs)`로 명시
    - 결과 보고 메시지 예시 앞에 `[specs]` 접두 추가
    - `vault-name` 변수 등장 위치를 backend=obsidian 분기 본문 안으로 한정 (Step 1의 컨텍스트 인자 목록은 유지 가능하나, "vault-name" 단어 사용을 obsidian 절로 한정)
    - 본문에서 "scripts", "django command", "manage.py", "bash", "Makefile" 등 scripts 트리거 단어 0건 유지(현 상태 확인)
  - `save-idea/SKILL.md`:
    - 첫 단락의 "Obsidian vault 또는 로컬 파일시스템에 저장하는 skill" → "선택된 백엔드(obsidian / filesystem / git)에 저장하는 skill"
    - 본문 어디에도 scripts 영역 트리거 단어가 없도록 확인(현재 0건 예상)
    - 결과 보고에 `[ideas]` 또는 별도 라벨은 도입하지 않음 — 영향 범위 최소화, FR-7는 specs/scripts 격리만 다룸
- **Validation**:
  - `grep -nE "scripts|django command|manage\.py|Makefile" sync-specs/SKILL.md` 0건
  - `grep -nE "scripts|django command|manage\.py|Makefile" save-idea/SKILL.md` 0건
  - 두 파일에서 첫 단락이 백엔드 중립 문장으로 시작
- **Complexity**: Simple

### Step 7: `plugin.json` 업데이트 (v2.1.0 + 백엔드 중립 description/keywords)

- **Goal**: 메타데이터를 갱신하고, description/keywords를 백엔드 중립으로 정리한다.
- **Specs Reference**: specs.md "Backend-neutral framing (FR-8) §plugin.json"
- **Files**:
  - `plugins/local-memory/plugin.json` — Modify
- **Details**:
  - `version`: `"2.0.0"` → `"2.1.0"`
  - `description`: `"GitHub repo 단위 외부기억을 Obsidian vault 또는 로컬 파일시스템에 저장·관리하는 플러그인"` → `"GitHub repo 단위 외부기억(specs · scripts · ideas)을 선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 플러그인"`
  - `keywords`: `["obsidian", "memory", "vault", "repo-context", "filesystem"]` → `["memory", "repo-context", "specs", "scripts", "obsidian", "filesystem", "git"]`
  - 다른 필드(name, author, homepage, repository, license)는 변경 없음
- **Validation**:
  - `jq '.version' plugin.json` 출력 `"2.1.0"`
  - `jq '.keywords' plugin.json` 출력 순서가 영역(specs/scripts) 우선, 백엔드는 그 뒤
- **Complexity**: Simple

### Step 8: `README.md` 업데이트 (Scripts Management 섹션 + datamaker-docs 예시 + FR-8 중립화)

- **Goal**: README의 헤드라인·개요·예시·표를 백엔드 중립으로 정리하고, 신규 `/sync-scripts` 명령어와 `scripts/` 폴더 구조를 1급으로 소개한다.
- **Specs Reference**: specs.md "Backend-neutral framing (FR-8) §README.md", FR-2/FR-3 acceptance criteria
- **Files**:
  - `plugins/local-memory/README.md` — Modify
- **Details**:
  - 헤드라인 문장: "선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 Claude Code 플러그인입니다."
  - 두 번째 단락: "스토리지 백엔드를 선택할 수 있어 Obsidian이 없는 서버 환경에서도 사용할 수 있습니다." → "백엔드(obsidian / filesystem / git)를 선택할 수 있으며, `datamaker-docs` 같은 git 저장소를 외부기억으로 그대로 사용할 수도 있습니다."
  - **"Backend 설정" 절 재배치**: 세 백엔드 예시 블록의 순서를 알파벳 순(`filesystem` → `git` → `obsidian`)으로 변경하고, "(기본값)" 라벨 제거. 대신 절 끝에 한 줄 Note:
    ```markdown
    > Note: `backend` 미설정 시 동작 호환성을 위해 `obsidian`이 사용됩니다. 신규 사용자는 `/check-settings`로 명시적으로 선택하세요.
    ```
  - "git" 백엔드 예시의 `basePath`를 `"/Users/jongtaek.hwang/Projects/datamaker-docs"`로 변경하고 `gitRemote`는 `"origin"`. 한 줄 주석: `// 실제 운영 예시 — datamaker-docs를 외부기억으로 활용`
  - "설정 항목" 표의 `backend` 행 기본값 표기는 그대로 유지(`obsidian`)하되, 표 각주로 "(기본값은 호환성용. `/check-settings`로 명시 선택 권장)" 추가
  - "명령어" 표에 `/sync-scripts [path|glob] [--category ...]` 행 추가
  - **새 절 "Scripts Management"** 추가 (명령어 표 직후):
    ```markdown
    ## Scripts Management

    `/sync-scripts`는 저장소의 스크립트를 외부기억의 `scripts/` 트리에 동기화합니다.

    | 카테고리 | 인식 규칙 | 저장 위치 |
    |---------|---------|---------|
    | bash | `scripts/**/*.sh`, `bin/**/*.sh` | `{repo}/scripts/bash/` |
    | makefile | `Makefile`, `*.mk` | `{repo}/scripts/makefile/` |
    | django-command | `**/management/commands/*.py` | `{repo}/scripts/django-command/{app}/` |

    > 인식 규칙·자연어 의도 매핑 전문은 `references/script-sources.md` 참조.
    >
    > spec 문서 동기화는 `/sync-specs`를 사용하세요 — 두 영역은 별도 skill로 분리되어 있습니다.
    ```
  - "폴더 구조" 섹션의 두 트리(`obsidian`, `filesystem / git`) 모두에 `scripts/{bash,makefile,django-command}/...`를 `specs/` 다음에 추가
  - vault 예시명: obsidian 예시는 `MyVault`로 유지하고, git 예시 옆에 `# 예: /Users/jongtaek.hwang/Projects/datamaker-docs` 주석을 명시
- **Validation**:
  - `grep -n "Obsidian이 없는" README.md` 0건
  - `grep -n "datamaker-docs" README.md` ≥ 1건
  - `## Scripts Management` 섹션 존재, `/sync-scripts` 표 행 존재
  - 폴더 구조 트리에 `scripts/` 포함
- **Complexity**: Medium

### Step 9: 사용자 업그레이드 동선 — README v2.0.0 → v2.1.0 노트 (FR-9)

- **Goal**: 기존 사용자가 안전하게 업그레이드할 수 있도록 README에 업그레이드 노트 절을 추가한다. 본 노트는 Step 8과 같은 파일을 편집하지만 별도 절로 두어 책임 경계를 분리한다.
- **Specs Reference**: specs.md "Plugin Update Migration (FR-9) §README 업그레이드 노트", FR-9 acceptance "README 업그레이드 노트"
- **Files**:
  - `plugins/local-memory/README.md` — Modify (Step 8과 동일 파일, 별도 절)
- **Details**:
  - 파일 하단(라이선스 직전)에 새 절 추가:
    ```markdown
    ## v2.0.0 → v2.1.0 업그레이드

    본 업데이트는 기존 데이터를 손상시키지 않습니다.

    - 기존 `.claude/local-memory.json` 그대로 동작합니다
    - 기존 `{directory}/{repo}/specs/`, `ideas/`, 인덱스 노트는 보존됩니다
    - 신규 `scripts/` 트리와 인덱스 `## Scripts` 섹션은 처음 `/sync-scripts`를 실행할 때 자동 생성됩니다
    - 진단: `/check-settings`의 "마이그레이션 감사" 절 확인
    - datamaker-docs의 루트 `django-commands/` 트리를 사용 중이라면 별도 가이드 참조: `docs/migrations/datamaker-docs-django-commands.md`
    - 다운그레이드 안전성: 추가된 `## Scripts` 섹션은 v2.0.0에서도 단순 마크다운으로 무해
    ```
  - 본 절은 Step 8의 Scripts Management/폴더 구조 갱신과 함께 한 PR에 포함하되, 별도 ### 레벨 헤딩으로 책임 경계를 명확히
- **Validation**:
  - `grep -n "v2.0.0 → v2.1.0" README.md` 1건 이상
  - 절 내 6개 bullet 모두 존재
- **Complexity**: Simple

### Step 10: 레거시 마이그레이션 가이드 작성

- **Goal**: datamaker-docs의 루트 평면 `django-commands/` 트리를 `{repo}/scripts/django-command/{app}/` 구조로 옮기는 사용자 수동 절차를 문서화. 자동 변환은 제공하지 않음. 본 가이드는 FR-9의 자동 lazy-migration 범위 밖이며 사용자 수동 작업임을 명시.
- **Specs Reference**: requirements.md FR-3 acceptance #5–#6, FR-9 "datamaker-docs 분리 명시", specs.md "Legacy reference (datamaker-docs)" 마이그레이션 매핑 표
- **Files**:
  - `docs/migrations/datamaker-docs-django-commands.md` — Create
- **Details**:
  - 섹션: (1) 배경, (2) 영향 범위, (3) 사전 검사, (4) 변환 절차, (5) 검증, (6) 정리(원본 트리 제거)
  - 배경: 본 plan/spec 요약, 왜 재분류가 필요한지(FR-1/FR-3 인용)
  - 영향 범위: `/Users/jongtaek.hwang/Projects/datamaker-docs/django-commands/{도메인}/*.py`. 도메인 14개 명시(celery, import, export, statistics, plugin, assignment, file-operations, data-files, format-conversion, project-specific, rapa-project, setup, utility, 그 외 추가 도메인은 실행 시 확인)
  - 사전 검사: `synapse-backend` repo 인덱스/스크립트 초기화 여부(`repo-memory` 사용)
  - 변환 절차(수동):
    1. `synapse-backend` 외부기억 트리 초기화 (해당 repo에서 `/check-settings` 또는 `/sync-scripts --category django-command` 1회 실행)
    2. 각 `django-commands/{도메인}/<command>.py`에 대해:
       - 새 파일 경로: `datamaker-docs/{directory}/synapse-backend/scripts/django-command/{도메인}/<command>.md`
       - frontmatter: `source_path`, `script_type: django-command`, `repo: synapse-backend`, `synced_at`, `tags`
       - 본문: `# {original 파일명}` + `​```python` 펜스 안에 원본 코드
    3. git 백엔드 사용 중인 경우 단일 커밋 메시지: `local-memory: migrate django-commands to scripts/django-command`
  - 검증: 변환된 파일 수 = 원본 `.py` 수(제외: `__init__.py`), frontmatter 필드 모두 채워졌는지 spot check
  - 정리: 검증 완료 후 사용자가 `git rm -r django-commands/` 또는 동등 명령으로 레거시 트리 제거
  - 명시: "본 plugin 코드는 자동 마이그레이션을 수행하지 않습니다. 안전성을 위해 모든 변환은 사용자가 직접 수행하며, 본 가이드의 명령을 차례대로 실행합니다."
- **Validation**:
  - 파일 존재, 6개 절 포함
  - 매핑 표가 1개 이상 예시 포함
- **Complexity**: Medium

## Task Breakdown

- [X] **Step 1**: `references/script-sources.md` 생성 (카테고리 표 + 인코딩 규칙 + 의도 사전)
- [X] **Step 2**: `references/backend-operations.md`에 scope-aware SEARCH 표 추가
- [X] **Step 3**: `agents/repo-memory/AGENT.md` scope/scripts 초기화/`[specs]`·`[scripts]` 라벨/중립화
- [X] **Step 4**: `commands/check-settings.md` Django 휴리스틱/scripts 헬스체크/메시지 분리/중립화
- [X] **Step 5**: `skills/sync-scripts/SKILL.md` 신규 작성 (FR-7 격리)
- [X] **Step 6**: `skills/sync-specs/SKILL.md` + `skills/save-idea/SKILL.md` 격리·중립화 정리
- [X] **Step 7**: `plugin.json` v2.1.0 + 중립 description/keywords
- [X] **Step 8**: `README.md` Scripts Management 섹션 + datamaker-docs 예시 + 중립화
- [X] **Step 9**: `README.md`에 v2.0.0 → v2.1.0 업그레이드 노트 절 추가
- [X] **Step 10**: `docs/migrations/datamaker-docs-django-commands.md` 신규 작성
- [ ] **Final**: 본 plan의 Acceptance Criteria Checklist 전 항목 검증 (라이브 호출 검증은 사용자 환경에서 진행 필요)

## File Change Summary

| File | Action | Step | Description |
|------|--------|------|-------------|
| `plugins/local-memory/references/script-sources.md` | Create | 1 | 카테고리 정의·인코딩·의도 사전 |
| `plugins/local-memory/references/backend-operations.md` | Modify | 2 | scope-aware SEARCH 표 추가, 링크 형식 노트 보강 |
| `plugins/local-memory/agents/repo-memory/AGENT.md` | Modify | 3 | scope 계약, scripts 초기화, 라벨, FR-8 중립화, **인덱스 노트 비파괴 병합(FR-9)** |
| `plugins/local-memory/commands/check-settings.md` | Modify | 4 | Django 휴리스틱, scripts 헬스체크, 라벨 분리, FR-8 중립화, **마이그레이션 감사 절(FR-9)** |
| `plugins/local-memory/skills/sync-scripts/SKILL.md` | Create | 5 | 신규 skill, FR-7 격리 준수 |
| `plugins/local-memory/skills/sync-specs/SKILL.md` | Modify | 6 | `scope=specs` 명시, `[specs]` 라벨, FR-8 중립화 |
| `plugins/local-memory/skills/save-idea/SKILL.md` | Modify | 6 | FR-8 중립화 (description) |
| `plugins/local-memory/plugin.json` | Modify | 7 | v2.1.0 + description + keywords |
| `plugins/local-memory/README.md` | Modify | 8 | 헤드라인/Backend 설정/명령어 표/폴더 구조/Scripts Management/예시에 datamaker-docs |
| `plugins/local-memory/README.md` | Modify | 9 | v2.0.0 → v2.1.0 업그레이드 노트 절 추가 (FR-9) |
| `docs/migrations/datamaker-docs-django-commands.md` | Create | 10 | 레거시 → scripts/django-command 사용자 마이그레이션 가이드 |

## Dependencies Between Steps

```
Step 1 ── Step 5 ── Step 8 ── Step 9 ─┐
   │         │                        │
   └── Step 2 ── Step 3 ── Step 4 ─┐  │
                                   ├──┴── Step 7 ── Step 8 ── Step 9
   Step 6 ─────────────────────────┘
   Step 10 (independent, can run anytime after Step 1)
```

- **Step 1** 선행: 모든 후속 단계가 카테고리/scope/의도 사전을 참조
- **Step 2** 선행: Step 3(AGENT)·Step 5(SKILL)이 scope-aware SEARCH 표를 인용
- **Step 3** 선행: Step 4(check-settings)·Step 5(SKILL)이 scope 계약과 인덱스 노트 병합 알고리즘을 호출
- **Step 5, 6** 병렬 가능 (서로 다른 파일, 같은 FR-7 규칙)
- **Step 7 → 8 → 9** 순차 (모두 같은 릴리스 단위의 메타·README 편집). Step 9는 Step 8과 같은 파일이지만 별도 절이므로 같은 PR에서 연속 편집
- **Step 10** 독립 — Step 1의 의도 사전과 specs.md 매핑 표만 있으면 작성 가능

## Testing Strategy

### Manual Verification

1. **플러그인 재설치 검증** — `/plugin install local-memory@orchwang-marketplace` 후 `/check-settings` 실행. `[specs]`/`[scripts]` 라벨 분리 출력 확인. Django 휴리스틱이 본 repo에서 INFO(MISSING)로 표시되는지 확인.
2. **scope-aware 검색 분리** — `repo-memory` 직접 호출 시 `scope=specs` / `scope=scripts` / `scope=all`이 각각 다른 경로를 검색하는지 backend별로 확인.
3. **filesystem 백엔드 sync-scripts** — `backend: "filesystem"`에서 본 마켓플레이스 repo로 `/sync-scripts` 실행. `{basePath}/{directory}/orchwang-claude-marketplace/scripts/{bash,makefile}/...` 파일 생성 확인.
4. **obsidian 백엔드 sync-scripts** — `backend: "obsidian"`에서 동일 시나리오. vault 내 노트 생성 및 `scope=scripts` SEARCH 작동 확인.
5. **git 백엔드 단일 커밋+push** — `backend: "git"`에서 `/sync-scripts` → 모든 파일 작성 후 단일 커밋 발생 확인.
6. **부분 동기화** — `/sync-scripts scripts/deploy --category bash` 같은 인자 범위 한정 확인.
7. **회귀 — `/sync-specs`, `/save-idea`** — 기존 동작 무회귀. 두 skill 결과 메시지에 scripts 트리거 단어 0건 유지.
8. **혼동 회귀 (FR-7)** — 자연어 "django command를 동기화해줘" / "manage.py 명령들 저장해" / "Makefile 저장" 입력 시 에이전트가 `sync-scripts`(scope=scripts)로 라우팅하는지 확인. specs 트리거 ("requirements 동기화") 입력은 `sync-specs`(scope=specs)로 라우팅.
9. **레거시 마이그레이션 리허설** — datamaker-docs의 `django-commands/celery/verify_beat_schedules.py` 1건을 가이드 절차대로 `synapse-backend/scripts/django-command/celery/verify_beat_schedules.md`로 변환. frontmatter 필드·코드 펜스·경로 일치 확인.
10. **표면 텍스트 중립성 리뷰 (FR-8)** — 다음 grep이 모두 0건이어야 함:
    - `grep -rn "Obsidian이 없는" plugins/local-memory`
    - `grep -rn "Vault 설정 읽기" plugins/local-memory`
    - `grep -rn "vault-name" plugins/local-memory/agents/repo-memory/AGENT.md` 가 obsidian 분기 외부에서 등장하지 않음
    - README 헤드라인을 처음 읽는 신규 사용자가 어느 한 백엔드도 1순위로 인지하지 않도록 표현이 균형 잡혔는지 가벼운 동료 리뷰
11. **업그레이드 시나리오 (FR-9) — 기존 사용자 데이터 무영향**:
    - v2.0.0 상태의 외부기억(예: 임시 fixture로 `{basePath}/{directory}/test-repo/{specs/, ideas/, test-repo.md}`를 미리 생성)을 두고 v2.1.0 플러그인으로 전환
    - 첫 동작이 `/check-settings`이면: 데이터 무변경 + "마이그레이션 감사" 절에 `## Scripts` MISSING, `scripts/` MISSING이 OK 외 상태로 보고되는지 확인
    - 첫 동작이 `/sync-specs`이면: 기존 specs 파일 frontmatter `synced`만 갱신, 본문은 source-of-truth로 덮어쓰기, 인덱스 노트 무변경
    - 첫 동작이 `/sync-scripts`이면: `scripts/` 트리 lazy-create + 인덱스 노트에 `## Scripts` 섹션 한 번만 비파괴 append. 사용자가 인덱스에 미리 넣어둔 임의 섹션(예: `## Notes`)은 그대로 보존
    - `/sync-scripts` 재실행 시 인덱스 노트가 추가 변경되지 않음(idempotency)
12. **다운그레이드 안전성 (FR-9)**: v2.1.0이 만든 인덱스 노트(`## Scripts` 섹션 포함)를 v2.0.0의 sync-specs/save-idea로 다시 처리해도 오류·데이터 손상이 없는지 확인 — 본 spec은 코드 로직이 없으므로 obsidian/markdown 렌더링 점검 정도로 충분

> 본 플러그인은 코드 로직이 없는 마크다운 spec 기반이므로 별도 단위/통합 테스트 스위트는 없다. 모든 검증은 Claude Code 내 실제 호출로 수행한다.

## Rollback Plan

각 단계별 안전한 복원 절차:

1. **Step 1–2 후 롤백**: 신규 `references/script-sources.md` 삭제, `references/backend-operations.md`는 `git checkout HEAD -- references/backend-operations.md`로 복원
2. **Step 3 후 롤백**: `agents/repo-memory/AGENT.md`를 직전 커밋으로 복원
3. **Step 4 후 롤백**: `commands/check-settings.md`를 직전 커밋으로 복원
4. **Step 5 후 롤백**: `skills/sync-scripts/` 디렉토리 전체 삭제
5. **Step 6 후 롤백**: `skills/sync-specs/SKILL.md`, `skills/save-idea/SKILL.md`를 직전 커밋으로 복원
6. **Step 7 후 롤백**: `plugin.json`의 `version`을 `"2.0.0"`로 되돌리고 description/keywords 복원
7. **Step 8 후 롤백**: `README.md`를 직전 커밋으로 복원
8. **Step 9 후 롤백**: `README.md`의 업그레이드 노트 절만 제거(`git checkout HEAD -- README.md` 또는 부분 revert)
9. **Step 10 후 롤백**: `docs/migrations/datamaker-docs-django-commands.md` 삭제

전체 롤백: `git checkout HEAD~N -- plugins/local-memory docs/migrations` (N = 본 작업 커밋 수)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 자연어 의도 사전이 사용자 표현을 충분히 커버하지 못해 잘못된 scope로 라우팅 | Medium | Medium | Step 1의 의도 사전을 실사용 피드백으로 주기적 보강. Step 8 Risk 절에 사용자 보고 채널 명시 |
| 거대한 스크립트 트리에서 `find` 성능 저하 | Low | Low | `--category` 인자로 범위 제한 권장. 향후 `--since <ref>` 도입 시 개선 |
| `<relpath-encoded>` 충돌(파일명 길이 초과) | Low | Medium | 본 작업에서는 fallback 미구현. 발생 시 명확한 오류 메시지 출력하고 사용자가 경로를 단축하도록 유도 |
| 레거시 datamaker-docs 마이그레이션 중 원본 `.py` 분실 | Medium | High | 가이드에 "검증 완료 전 원본 삭제 금지" 강조. 자동 변환 미제공 |
| `obsidian` 기본 백엔드 정책 변경이 기존 사용자에 영향 | Low | Medium | 동작 수준 기본값은 보존. `/check-settings` 신규 흐름만 명시 선택 유도 |
| FR-8 중립화 작업 중 본문 의미 변형 | Low | Medium | grep 기반 리뷰 체크리스트(Test #10)로 정량 검증 |
| Django command 카테고리 파일명 규칙(`{app}/<command>.md`)이 다른 카테고리와 불일치 | Low | Low | Step 1 문서에 명시하고 Step 5 SKILL에서 분기 처리. 향후 통일 검토는 Open Question으로 남김 |
| 인덱스 노트 비파괴 병합 중 사용자가 작성한 커스텀 섹션 손상 (FR-9) | Low | High | 헤딩 라인 단위 정확 일치 검출(`^## Scripts\s*$`), 본문 read-modify-write, `## Ideas` 직전 삽입. 테스트 #11에서 임의 `## Notes` 섹션 보존 검증 |
| `/sync-scripts` 첫 실행에서 인덱스 노트 부재 → 신규 템플릿 덮어쓰기로 인식되어 사용자 의도와 충돌 | Low | Medium | EXISTS 분기로 미존재시에만 신규 생성. README 업그레이드 노트(Step 9)에 동작 명시 |
| 레거시 `django-commands/` 평면 트리 감지 오탐(`basePath` 추측) | Low | Low | filesystem/git 백엔드 한정, `{basePath}` 직속에만 검사. INFO 상태로 보고하고 자동 동작 없음 |

## Progress Tracking

| Step | Status | Started | Completed | Notes |
|------|--------|---------|-----------|-------|
| Step 1: script-sources.md | Completed | 2026-05-13 | 2026-05-13 | grep 통과: 카테고리 11회, obsidian 우선 표현 0건 |
| Step 2: backend-operations.md scope | Completed | 2026-05-13 | 2026-05-13 | scope-aware SEARCH 표 추가, scope 3회 등장 |
| Step 3: AGENT.md (scope + scripts init + label + 중립화) | Completed | 2026-05-13 | 2026-05-13 | scope 14회, `[specs]`/`[scripts]` 라벨 6회, 비파괴 병합 절 추가, `Vault 설정 읽기` 0건 |
| Step 4: check-settings.md (Django 휴리스틱 + 헬스체크 + 라벨 + 중립화) | Completed | 2026-05-13 | 2026-05-13 | manage.py 검사, 영역별 헬스체크, 마이그레이션 감사 절, 기본값 무음 적용 금지 명시 |
| Step 5: sync-scripts/SKILL.md | Completed | 2026-05-13 | 2026-05-13 | `[scripts]` 5회, `scope=scripts` 3회, frontmatter 명세, specs 트리거 1건(허용된 경계 마커) |
| Step 6: sync-specs + save-idea 격리·중립화 | Completed | 2026-05-13 | 2026-05-13 | sync-specs에 `scope=specs`/`[specs]` 추가, scripts 트리거는 경계 마커 + 메타 라벨 안내만 잔존 |
| Step 7: plugin.json v2.1.0 | Completed | 2026-05-13 | 2026-05-13 | version 2.1.0, 중립 description, keywords 영역 우선 + 백엔드 알파벳 순 |
| Step 8: README.md (Scripts Management + datamaker-docs + 중립화) | Completed | 2026-05-13 | 2026-05-13 | datamaker-docs 4회, Scripts Management 섹션 신설, 폴더 트리에 scripts/ 포함, `Obsidian이 없는` 0건 |
| Step 9: README v2.0.0 → v2.1.0 업그레이드 노트 (FR-9) | Completed | 2026-05-13 | 2026-05-13 | Step 8과 같은 파일에 별도 절로 작성 |
| Step 10: docs/migrations/datamaker-docs-django-commands.md | Completed | 2026-05-13 | 2026-05-13 | 7개 절, datamaker-docs 8회·synapse-backend 11회 매핑 명시, 변환 스크립트 포함 |

## Acceptance Criteria Checklist

### FR-1: 스크립트 인식 범위
- [ ] bash 글롭 규칙(`scripts/**/*.sh`, `bin/**/*.sh`, 실행권한 `*.sh`) 문서화 (Step 1)
- [ ] makefile 규칙(`Makefile`, `*/Makefile`, `*.mk`) 문서화 (Step 1)
- [ ] django-command 규칙(`**/management/commands/*.py` 제외 `__init__.py`) 문서화 (Step 1)
- [ ] 향후 확장 후보(Justfile, npm scripts) 명시 (Step 1)
- [ ] 인식 규칙이 단일 레퍼런스 문서로 존재 (Step 1)
- [ ] 루트 평면 `django-commands/` 미인식 명시 (Step 1)

### FR-2: sync-scripts skill
- [ ] `skills/sync-scripts/SKILL.md` 존재 (Step 5)
- [ ] git repo 자동 감지 + 인식 규칙 매칭 (Step 5)
- [ ] 저장 경로 `{directory}/{repo}/scripts/{카테고리}/...` (Step 5)
- [ ] 코드 펜스로 원본 보존 (Step 5)
- [ ] frontmatter `source_path`, `script_type`, `synced_at`, `repo` (Step 5)
- [ ] 부분 동기화 인자 지원 (Step 5)

### FR-3: 폴더 구조 확장
- [ ] `repo-memory`가 `scripts/` 디렉토리 초기화 (Step 3)
- [ ] obsidian 백엔드 구조 명시 (Step 3, 8)
- [ ] filesystem/git 백엔드 구조 명시 (Step 3, 8)
- [ ] 인덱스 노트에 `scripts/` 링크 추가 (Step 3)
- [ ] 루트 평면 카테고리 폴더 생성·인식 금지 (Step 1, 3)
- [ ] 레거시 마이그레이션 가능성 명시 (Step 9)

### FR-4: scope 검색 구분
- [ ] `scope: specs | scripts | all` 개념 지원 (Step 3)
- [ ] 백엔드별 SEARCH 분기 (Step 2)
- [ ] `save-idea`(별개) 무영향 (Step 6)

### FR-5: check-settings 확장
- [ ] scripts 트리 쓰기 권한/통신 확인 (Step 4)
- [ ] Django 휴리스틱 정보성 보고 (Step 4)

### FR-6: repo-memory 분기 확장
- [ ] 폴더 초기화에서 `scripts/<카테고리>/` 생성 (Step 3)
- [ ] 인덱스 노트 링크 분기 유지 (Step 3)
- [ ] `scope` 인자 → 백엔드 명령 변환 책임 (Step 3)

### FR-7: 지시문 격리
- [ ] skill 파일 분리·cross-reference 금지 (Step 5, 6)
- [ ] 어휘 분리(specs/scripts 트리거 단어 비혼합) (Step 5, 6)
- [ ] `scope` 라우팅 계약 + 모호 시 사용자 확인 (Step 3)
- [ ] 자연어 의도 사전 (Step 1)
- [ ] 출력 메시지 `[specs]`/`[scripts]` 라벨 (Step 3, 4, 5, 6)

### FR-8: 백엔드 중립화
- [ ] `plugin.json` description/keywords 중립 (Step 7)
- [ ] README 헤드라인/개요 중립 (Step 8)
- [ ] Backend 설정 예시 균등, `(기본값)` 라벨 제거 (Step 8)
- [ ] vault 예시명에 `datamaker-docs` 병기 (Step 8)
- [ ] AGENT/SKILL/command 본문 중립화 (Step 3, 4, 6)
- [ ] 신규 sync-scripts 산출물 초기 중립 (Step 1, 5, 10)
- [ ] 기본 백엔드 정책 — 동작 호환 유지, `/check-settings` 명시 선택 유도 (Step 4, 8)

### FR-9: Plugin Update Migration
- [ ] 설정 파일 호환 — v2.0.0 `.claude/local-memory.json` 무수정 동작 (Step 4, 8: Note 명시 + 변경 부재 검증)
- [ ] 기존 specs/ideas/인덱스 트리 무손상 — 업그레이드 행위 자체에 쓰기 없음 (전 단계 공통 원칙)
- [ ] scripts/ 트리 lazy-create — `/sync-scripts` 또는 scope=scripts|all 호출 시에만 생성 (Step 3)
- [ ] 인덱스 노트 비파괴 병합 — `## Ideas` 직전(또는 본문 끝)에 `## Scripts` 한 번만 append (Step 3)
- [ ] 인덱스 노트 부재 시 신규 템플릿 (specs/scripts/ideas 3섹션) 생성 (Step 3)
- [ ] `/check-settings` 마이그레이션 감사 절 출력 (Step 4)
- [ ] Idempotency — 재실행 시 중복 생성·인덱스 추가 변경 없음 (Step 3, 4, 5)
- [ ] README 업그레이드 노트 절 추가 (Step 9)
- [ ] datamaker-docs `django-commands/`는 자동 마이그레이션 대상 아님 명시 (Step 9, 10)
- [ ] 다운그레이드 안전성 — v2.1.0 산출물(`## Scripts` 섹션)이 v2.0.0에서 무해 (Step 9 노트 + Testing #12)
