# Specs: Sync scripts for local-memory plugin

> Created: 2026-05-13
> Updated: 2026-05-13
> Status: Draft
> Requirements: [requirements.md](./requirements.md)

## Overview

> TBD — `/sdd-helper:specify-with-requirements`로 채워집니다.

requirements.md에서 정의된 9개 FR을 기술 사양으로 구체화한다. 핵심 결정 사항:

1. 스크립트 인식 규칙을 단일 레퍼런스(`references/script-sources.md`)로 분리
2. `sync-scripts` skill을 `sync-specs`와 동일한 4단계 흐름으로 구현
3. `scope` 개념(`specs` / `scripts` / `all`)을 `repo-memory` 에이전트 계약에 추가
4. 백엔드별 명령 매핑은 기존 `backend-operations.md`에 `scope` 차원만 추가
5. specs/scripts 지시문 격리 — 두 skill 파일은 어휘·트리거 단어·동작 설명을 분리하여 에이전트 라우팅 혼동을 차단
6. 플러그인 표면 텍스트(설명/키워드/README/AGENT/SKILL/command) 백엔드 중립화 — obsidian/filesystem/git 3종을 동등하게 노출하고, datamaker-docs 같은 git 저장소를 1급 예시로 채택
7. 기존 사용자 데이터(specs/, ideas/, 인덱스 노트, 설정 파일)에 대한 비파괴 lazy-migration 전략 — 업그레이드는 데이터를 건드리지 않고, scripts/ 트리·인덱스 `## Scripts` 섹션은 사용자가 skill을 호출하는 시점에만 추가

### Legacy reference (datamaker-docs)

설계 검증을 위해 `/Users/jongtaek.hwang/Projects/datamaker-docs` 실제 구조를 참조한다.

관찰된 레거시 레이아웃:

```
/Users/jongtaek.hwang/Projects/datamaker-docs/
├── specs/synapse-backend/{feature}/...         # 정상: repo-scoped
└── django-commands/{도메인}/<command>.py        # 평면 (이번 작업으로 재분류)
```

마이그레이션 매핑(권장):

| 레거시 경로 | 새 경로 |
|------------|--------|
| `datamaker-docs/django-commands/celery/verify_beat_schedules.py` | `datamaker-docs/synapse-backend/scripts/django-command/celery/verify_beat_schedules.md` |
| `datamaker-docs/django-commands/import/local_default_import.py` | `datamaker-docs/synapse-backend/scripts/django-command/import/local_default_import.md` |
| `datamaker-docs/django-commands/<도메인>/<command>.py` | `datamaker-docs/synapse-backend/scripts/django-command/<도메인>/<command>.md` |

- 원본 `.py` 코드는 새 위치의 `.md` 본문 안 `​```python` 펜스로 보존
- frontmatter에 `source_path`(원래 repo 내 management/commands 경로), `script_type: django-command`, `repo: synapse-backend` 기록
- 레거시 평면 트리 자체는 마이그레이션 가이드에 따라 별도 삭제 (이번 plugin 코드 변경이 자동 삭제하지 않음)

## Technical Specifications

### Script Source Reference

`plugins/local-memory/references/script-sources.md` (신규)에 카테고리별 인식 규칙을 정의:

| 카테고리 | 글롭/규칙 | 저장 카테고리 디렉토리 | 코드 펜스 |
|---------|----------|---------------------|----------|
| Bash/Shell | `scripts/**/*.sh`, `bin/**/*.sh`, 실행권한 `*.sh` | `scripts/bash/` | `​```bash` |
| Makefile | `Makefile`, `*/Makefile`, `*.mk` | `scripts/makefile/` | `​```makefile` |
| Django command | `**/management/commands/*.py` (제외: `__init__.py`) | `scripts/django-command/` | `​```python` |

> 추가 카테고리(justfile, npm scripts)는 표 확장만으로 합류 가능하도록 동일 스키마 유지.

### Storage Layout

```
{directory}/{repo-name}/
  {repo-name}.md          # 인덱스 (specs / scripts / ideas 섹션)
  specs/
    {task-name}/...
  scripts/
    bash/
      <relpath-encoded>.md
    makefile/
      <relpath-encoded>.md
    django-command/
      <app>__<command>.md
  ideas/
    {idea-slug}.md
```

- `<relpath-encoded>`: 원본 상대경로의 `/`를 `__`로 치환하여 파일명 충돌 방지
  - 예: `scripts/deploy/run.sh` → `scripts__deploy__run.md`
- 노트 본문 구조:

  ```markdown
  ---
  source_path: scripts/deploy/run.sh
  script_type: bash
  repo: orchwang-claude-marketplace
  synced_at: 2026-05-13T10:00:00+09:00
  ---

  # scripts/deploy/run.sh

  ​```bash
  <원본 그대로>
  ​```
  ```

### `repo-memory` 에이전트 계약 확장

- 호출 인자에 `scope: "specs" | "scripts" | "all"` 추가 (기본 `all`)
- Pre-flight check, 폴더 초기화에서 `scripts/<카테고리>/` 디렉토리 생성 책임
- 백엔드별 SEARCH 분기에 scope 경로 매핑:

| Operation | scope | obsidian | filesystem / git |
|-----------|-------|----------|-----------------|
| SEARCH | specs | `obsidian search query="path:{directory}/{repo}/specs"` | `find "{basePath}/{directory}/{repo}/specs" -name "*.md"` |
| SEARCH | scripts | `obsidian search query="path:{directory}/{repo}/scripts"` | `find "{basePath}/{directory}/{repo}/scripts" -name "*.md"` |
| SEARCH | all | `obsidian search query="path:{directory}/{repo}"` | `find "{basePath}/{directory}/{repo}" -name "*.md"` |

### `sync-scripts` Skill 흐름

1. `repo-memory` 호출 → Pre-flight + repo 감지 + `scripts/<카테고리>/` 디렉토리 보장
2. 인자 파싱: `/sync-scripts [<glob-or-path>] [--category bash|makefile|django-command|all]`
3. `references/script-sources.md`의 규칙으로 후보 파일 수집
4. 파일별로 카테고리·코드 펜스·저장 경로 결정, frontmatter 생성
5. 백엔드별 CREATE 연산 호출 (obsidian/filesystem/git)
6. git 백엔드는 모든 파일 작성 후 단일 커밋 + push (기존 정책 재사용)
7. 결과 요약 출력: 카테고리별 개수, 실패 항목

### `/check-settings` 확장

- Step 1(환경): Django 휴리스틱(`manage.py` 존재) — 정보성 출력
- Step 5(연결 테스트): `scripts/.healthcheck.md` 생성/조회/삭제로 scripts 경로 쓰기 확인

### 링크 형식

- obsidian 백엔드: 인덱스에 `![[{directory}/{repo}/scripts]]` 추가
- filesystem/git 백엔드: 인덱스에 `[scripts](./scripts/)` 추가

### Instruction isolation (FR-7)

specs와 scripts 처리 지시문은 다음 원칙으로 격리한다:

1. **Skill 파일 분리·자기완결성**
   - `skills/sync-specs/SKILL.md`: spec 문서(requirements/specs/plans)만 다룬다. "scripts", "django command", "bash", "makefile" 등 트리거 단어 사용 금지.
   - `skills/sync-scripts/SKILL.md`: 스크립트만 다룬다. "requirements.md", "plans.md", "spec 문서" 등 specs 트리거 단어 사용 금지. cross-link 대신 별도 절(예: "다른 영역은 `sync-specs`를 사용하세요")로 한 줄 경계만 둠.

2. **scope 라우팅 계약**
   - `repo-memory` 에이전트는 `scope` 인자 없이 호출되면 사용자에게 명시적으로 묻는다 — "specs / scripts / all 중 어느 범위를 동기화·검색할까요?"
   - skill에서 호출 시 항상 `scope`를 명시: `sync-specs` → `scope=specs`, `sync-scripts` → `scope=scripts`.

3. **자연어 의도 사전 (intent dictionary)**
   - `references/script-sources.md`에 사용자 표현 → scope 매핑 테이블을 둔다:

     | 사용자 표현 | scope |
     |------------|-------|
     | "django command", "manage.py", "management command" | scripts |
     | "bash 스크립트", "shell 스크립트", "*.sh" | scripts |
     | "Makefile", "make 타겟" | scripts |
     | "requirements", "specs", "plans", "spec 문서", "스펙" | specs |
     | "메모", "아이디어" | (별도 `save-idea`) |

4. **출력 메시지 라벨링**
   - 에이전트 및 skill의 진행/오류 메시지에는 `[specs]` 또는 `[scripts]` 라벨을 접두로 둔다. 예: `[scripts] 3 files discovered (bash: 2, makefile: 1)`.

5. **Pre-flight check 메시지 분리**
   - specs 트리 미존재와 scripts 트리 미존재는 서로 다른 오류 메시지로 보고하며 한 메시지에서 두 영역을 동시에 언급하지 않는다.

### Backend-neutral framing (FR-8)

표면 텍스트를 obsidian-우선에서 백엔드 중립으로 정리한다. 구체 변경안:

#### `plugin.json`

- `description`: `"GitHub repo 단위 외부기억을 Obsidian vault 또는 로컬 파일시스템에 저장·관리하는 플러그인"` → `"GitHub repo 단위 외부기억을 선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 플러그인"`
- `keywords`: `["obsidian", "memory", "vault", "repo-context", "filesystem"]` → `["memory", "repo-context", "obsidian", "filesystem", "git", "scripts"]` (영역명 우선, 백엔드는 알파벳 순)

#### `README.md`

- 헤드라인 문장: `"… Obsidian vault 또는 로컬 파일시스템에 저장·관리하는 …"` → `"… 선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 …"`
- 두 번째 단락: `"스토리지 백엔드를 선택할 수 있어 Obsidian이 없는 서버 환경에서도 사용할 수 있습니다."` → `"백엔드(obsidian / filesystem / git)를 선택할 수 있으며, datamaker-docs 같은 git 저장소를 외부기억으로 사용할 수도 있습니다."`
- "Backend 설정" 절: 세 백엔드 예시 블록(`obsidian` / `filesystem` / `git`)을 동일 비중으로 노출. `### obsidian (기본값)` 라벨에서 "(기본값)" 제거하고, "기본 백엔드" 안내는 별도 주석/Note 박스로 분리
- vault 예시명 `MyVault` → 한쪽에는 `MyVault`(obsidian 예시) 유지, 다른쪽에는 `datamaker-docs`(git 백엔드 예시) 병기
- 설정 표 각주: "(기본값: `obsidian`)"은 표 한 줄로 유지하되, 위계적 강조 어휘는 제거

#### `agents/repo-memory/AGENT.md`

- frontmatter `description`: `"… Obsidian vault 또는 로컬 파일시스템에 관리하는 에이전트"` → `"… 선택된 백엔드(obsidian / filesystem / git)에 관리하는 에이전트"`
- 본문 첫 단락 동일 수정
- 섹션 헤더 `## Vault 설정 읽기` → `## 백엔드 설정 읽기`
- 본문 내 "vault-name" 변수 표기는 obsidian 분기 안에서만 등장하도록 제한 (공통 절은 `{backend-target}` 등 추상명 사용)

#### `skills/sync-specs/SKILL.md` / `skills/save-idea/SKILL.md`

- frontmatter description의 "Obsidian vault 또는 로컬 파일시스템" 표현을 백엔드 중립으로 변경 ("선택된 백엔드")
- Pre-flight 절의 `vault-name` 변수 노출을 백엔드별 분기 내부로 제한

#### `commands/check-settings.md`

- 본문 안내 메시지 중 "Obsidian이 없는 환경에서도" 같은 위계 표현 제거
- 백엔드 선택 프롬프트에서 3종을 동일 비중으로 제시 (`obsidian / filesystem / git`), 기본 옵션 추천이 필요할 경우 별도 주석으로 분리

#### 신규 sync-scripts 산출물

- `skills/sync-scripts/SKILL.md`, `references/script-sources.md`, 마이그레이션 가이드(`docs/migrations/datamaker-docs-django-commands.md`)는 처음 작성 시부터 백엔드 중립 어조로 기술. 코드 펜스/예시도 obsidian과 git 예시를 동등 노출

#### 기본 백엔드 정책

- 호환성 유지를 위해 코드 수준 기본값(`backend` 미설정 시 `obsidian`)은 보존
- `/check-settings` 신규 사용자 흐름에서는 백엔드를 명시적으로 묻고, 기본값 무음 적용을 차단
- 이 결정은 README 표 각주와 별도 Note 박스로만 노출되며 본문 강조에서는 빠진다

### Plugin Update Migration (FR-9)

v2.0.0 → v2.1.0 업그레이드 시 기존 사용자 데이터를 비파괴 lazy-migrate 한다. 모든 쓰기는 사용자가 skill을 명시 호출하는 시점에만 발생.

#### 마이그레이션 매트릭스

| 자산 | v2.0.0 상태 | v2.1.0 동작 | 트리거 |
|------|-----------|-----------|-------|
| `.claude/local-memory.json` | 기존 필드(backend, vault, basePath, directory, gitAutoCommit, gitRemote) | 변경 없이 동작. 신규 필드 미추가 | 자동(읽기만) |
| `{directory}/{repo}/specs/...` | 기존 파일 다수 존재 | 변경 없음. `/sync-specs` 재실행 시 frontmatter `synced` 필드만 갱신, 본문 그대로 덮어쓰기 | `/sync-specs` 호출 |
| `{directory}/{repo}/ideas/...` | 기존 파일 다수 존재 | 변경 없음 | `/save-idea` 호출 |
| `{directory}/{repo}/{repo}.md` (인덱스 노트) | `## Specs`, `## Ideas` 섹션 보유 | `## Scripts` 섹션을 `## Ideas` 직전(또는 본문 끝)에 append. 사용자 추가 섹션·문구 보존 | `repo-memory(scope=scripts\|all)` 호출 |
| `{directory}/{repo}/scripts/...` | 미존재 | `/sync-scripts` 또는 `scope=scripts\|all` 호출 시 lazy-create | `/sync-scripts` 호출 |

#### 인덱스 노트 비파괴 병합 알고리즘

`repo-memory` 에이전트가 `scope=scripts` 또는 `scope=all`로 호출되면:

1. 인덱스 노트 존재 확인 (백엔드별 EXISTS 연산)
2. 미존재 → 신규 템플릿으로 생성 (specs / scripts / ideas 3섹션 포함)
3. 존재 → READ로 본문 로드
4. 본문에서 정확한 헤딩 `## Scripts`(앞뒤 공백 무시) 존재 여부 검사
5. 존재 → no-op
6. 부재 → 다음 마크다운 블록을 삽입:
   ```markdown
   ## Scripts

   ![[{directory}/{repo}/scripts]]   # obsidian
   ```
   또는 filesystem/git:
   ```markdown
   ## Scripts

   - [scripts](./{repo-name}/scripts/)
   ```
7. 삽입 위치: 본문 내 `## Ideas` 헤딩이 있으면 그 직전 빈 줄에 삽입, 없으면 본문 끝에 append
8. 백엔드별 CREATE(overwrite)로 노트 전체를 다시 쓴다. 다른 섹션·사용자 추가 텍스트는 모두 보존

> obsidian 백엔드의 `append` CLI를 쓰는 대안도 가능하지만, 삽입 위치 제어를 위해 본 명세는 read-modify-write를 채택한다.

#### `/check-settings` 마이그레이션 감사

`/check-settings`의 결과 출력에 신규 절을 추가:

```
## 마이그레이션 감사 (v2.0.0 → v2.1.0)
| 항목 | 상태 | 보강 명령 |
|------|------|----------|
| 인덱스 노트 | OK / MISSING | (MISSING) `/sync-scripts` 또는 `/save-idea` 1회 실행으로 자동 생성 |
| 인덱스 노트의 ## Scripts 섹션 | OK / MISSING | (MISSING) `/sync-scripts`(또는 빈 호출) 1회 실행 |
| {repo}/scripts/ 트리 | OK / MISSING | (MISSING) `/sync-scripts` 실행 시 자동 생성 |
| 레거시 루트 평면 트리(django-commands/) | INFO | (있으면) docs/migrations/datamaker-docs-django-commands.md 가이드 참조 |
```

레거시 평면 트리 감지는 filesystem/git 백엔드에서만 수행: `test -d "{basePath}/django-commands"` 같은 단순 검사. 위치는 `{basePath}/{directory}/...`가 아닌 `{basePath}` 직속(예: datamaker-docs 루트)임에 유의.

#### Idempotency 보장

- `/sync-specs` 재실행: 같은 task에 대해 frontmatter `synced` 날짜만 갱신, 본문은 source-of-truth(repo 내 specs/)로 덮어쓰기. 신규 파일·디렉토리 생성 없음.
- `/save-idea` 재실행: 동일 slug 검출 시 `overwrite` 여부를 사용자에게 묻는 기존 흐름 유지
- `repo-memory` 인덱스 노트 병합: 두 번째 호출부터는 Step 5(no-op)에서 종료

#### README 업그레이드 노트

README에 새 절 추가:

```markdown
## v2.0.0 → v2.1.0 업그레이드

본 업데이트는 기존 데이터를 손상시키지 않습니다.

- 기존 `.claude/local-memory.json` 그대로 동작합니다
- 기존 `{directory}/{repo}/specs/`, `ideas/`, 인덱스 노트는 보존됩니다
- 신규 `scripts/` 트리와 인덱스 `## Scripts` 섹션은 처음 `/sync-scripts`를 실행할 때 자동 생성됩니다
- 진단: `/check-settings`의 "마이그레이션 감사" 절 확인
- datamaker-docs의 루트 `django-commands/` 트리를 사용 중이라면 별도 가이드 참조: `docs/migrations/datamaker-docs-django-commands.md`
```

#### 다운그레이드 안전성

v2.1.0이 추가한 인덱스 `## Scripts` 섹션은 단순 마크다운 헤딩 + 링크이므로 v2.0.0(또는 obsidian-skills) 환경에서 그대로 읽힌다. 링크 대상(`scripts/` 경로)이 비어 있어도 obsidian/markdown 렌더링 오류는 발생하지 않는다.

## Architecture

### 파일 구조 (변경/추가)

```
plugins/local-memory/
  references/
    backend-operations.md    # scope 분기 표 추가
    script-sources.md        # NEW
  agents/repo-memory/
    AGENT.md                 # scope 인자, scripts 폴더 초기화
  commands/
    check-settings.md        # scripts 경로 검증, Django 휴리스틱
  skills/
    sync-specs/SKILL.md      # 변경 없음(또는 scope=specs 호출로 정규화)
    sync-scripts/SKILL.md    # NEW
    save-idea/SKILL.md       # 변경 없음
  plugin.json                # 버전업, sync-scripts skill 등록
  README.md                  # Scripts Management 섹션 추가
```

### 데이터 흐름

1. 사용자 `/sync-scripts` 호출
2. skill이 `repo-memory(scope=scripts)` 호출 → 백엔드/경로/권한 검증
3. skill이 `script-sources.md` 규칙으로 파일 수집
4. 파일별 frontmatter + 본문 합성
5. `backend-operations.md` 참조하여 CREATE 명령 실행
6. git 백엔드는 마지막에 커밋+push

## Error Handling

- 인식된 스크립트가 0개: "동기화할 스크립트가 없습니다. `references/script-sources.md`의 규칙을 확인하세요."
- 카테고리 인자가 유효하지 않음: "지원 카테고리: bash, makefile, django-command, all"
- 파일 읽기 실패(권한 등): 해당 파일만 스킵하고 결과 요약에 실패 목록 표시
- git 백엔드 커밋 실패: 부분 저장 상태를 명시하고 다음 실행에서 재시도 가능함을 안내

## Dependencies

- 기존 백엔드 의존성과 동일 (obsidian-skills, git CLI, POSIX `find`)
- 추가 의존성 없음

## Open Questions

- `<relpath-encoded>` 충돌 규칙으로 충분한가? 매우 깊은 경로 시 파일명 길이 한계 고려 여부
- Django command 카테고리 파일명에 app 식별자(`<app>__<command>.md`)를 강제할지, 일반 상대경로 인코딩과 통일할지
- `--category` 인자 외에 `--since <ref>` 같은 변경분 기반 동기화를 향후 도입할지
- datamaker-docs 레거시 `django-commands/` 마이그레이션을 일회성 스크립트로 제공할지, 가이드 문서만 둘지

> 위 항목은 `/sdd-helper:specify-with-requirements` 또는 `/sdd-helper:plan-with-specs` 단계에서 확정.

## Clarification Log

| # | 변경 사항 | 출처 | 일자 |
|---|----------|------|------|
| 1 | datamaker-docs 실제 구조 반영 — `django-commands/` 루트 평면 트리는 `scripts/django-command/`로 재분류 (FR-1, FR-3) | Applied via /update-requirements | 2026-05-13 |
| 2 | FR-7 추가 — specs/scripts 지시문 격리(어휘·skill 파일·scope·라벨 분리) | Applied via /update-requirements | 2026-05-13 |
| 3 | "Legacy reference (datamaker-docs)" 섹션 및 마이그레이션 매핑 표 추가 | Applied via /update-requirements | 2026-05-13 |
| 4 | "Instruction isolation (FR-7)" 섹션 추가 — 자연어 의도 사전, 출력 라벨, pre-flight 메시지 분리 | Applied via /update-requirements | 2026-05-13 |
| 5 | FR-8 추가 — 플러그인 표면 텍스트(설명/키워드/README/AGENT/SKILL/command)의 백엔드 중립화, datamaker-docs 1급 예시 노출 | Applied via /update-requirements | 2026-05-13 |
| 6 | "Backend-neutral framing (FR-8)" 섹션 추가 — 파일별 구체 변경안과 기본 백엔드 정책 명문화 | Applied via /update-requirements | 2026-05-13 |
| 7 | FR-9 추가 — Plugin v2.0.0 → v2.1.0 업그레이드 시 비파괴 lazy-migration 전략 | Applied via /update-requirements | 2026-05-13 |
| 8 | "Plugin Update Migration (FR-9)" 섹션 추가 — 마이그레이션 매트릭스, 인덱스 노트 병합 알고리즘, check-settings 감사 절, idempotency, 업그레이드 노트, 다운그레이드 안전성 | Applied via /update-requirements | 2026-05-13 |
