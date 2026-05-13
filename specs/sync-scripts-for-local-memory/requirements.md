# Requirements: Sync scripts for local-memory plugin

> Created: 2026-05-13
> Updated: 2026-05-13
> Status: Draft
> Ticket: N/A

## Overview

local-memory 플러그인은 현재 `specs/` 디렉토리의 문서(requirements, specs, plans)만 외부기억으로 동기화·관리한다. 그러나 실제 저장소에는 운영·개발 지식이 spec 문서 외에도 다양한 스크립트 형태로 존재한다: Django management command(`*/management/commands/*.py`), Bash 스크립트(`scripts/*.sh`), Makefile, npm scripts, Justfile 등.

이번 작업에서는 local-memory 플러그인이 `specs/`에 더해 저장소 내 스크립트도 식별·동기화·검색할 수 있도록 확장한다. 저장 시에는 `specs/`와 동일한 방식으로 repo 단위 폴더 구조에 `scripts/`를 분리하여 두며, 검색·조회도 `specs`/`scripts`를 구분하여 활용할 수 있어야 한다.

### Reference: 현재 local-memory 사용 실태 (datamaker-docs)

설계의 그라운드 트루스로 `/Users/jongtaek.hwang/Projects/datamaker-docs`에 실제로 적재되고 있는 local-memory 저장소 구조를 참조한다. 관찰된 핵심 사항:

```
datamaker-docs/
├── specs/
│   └── synapse-backend/{feature}/...        # repo-scoped specs (정상)
├── django-commands/                          # ⚠ 루트 레벨에 평면 존재
│   ├── celery/, import/, export/, statistics/, plugin/, ...
│   │   └── <command>.py                      # 원본 코드가 그대로 저장
│   └── ...
├── design/, knowledge/, meetings/, presentations/, templates/, prompts/
```

위 구조에서 두 가지 문제가 식별된다:

1. **카테고리 비일관성** — `django-commands/`가 루트 레벨에 평면으로 존재하며 `{repo-name}/scripts/` 하위 구조를 따르지 않는다. 이번 작업으로 `synapse-backend/scripts/django-command/{도메인}/...`로 재분류한다.
2. **지시문 혼동** — 현재 버전(`sync-specs` 단일 skill)에서는 사용자가 django-command 관리를 요청할 때 에이전트가 specs 관련 지시와 동일 흐름으로 해석하여 specs 폴더로 잘못 라우팅하는 경우가 많았다. 신규 `sync-scripts` skill과 `scope` 라우팅으로 혼동을 차단해야 한다.

## Goals

- [ ] 저장소 내 스크립트(`scripts/*.sh`, `Makefile`, Django management commands 등)를 local-memory 대상에 포함한다
- [ ] `sync-specs`와 대칭되는 `sync-scripts` skill을 제공한다
- [ ] 저장소 외부기억의 폴더 구조에 `scripts/`를 `specs/`와 나란히 둔다
- [ ] 검색·조회 시 `specs` / `scripts` 범위를 구분하여 지정할 수 있다
- [ ] 기존 `obsidian` / `filesystem` / `git` 3종 백엔드 모두에서 동작한다

## Functional Requirements

### FR-1: 스크립트 인식 범위 정의

- **Description**: local-memory가 "스크립트"로 간주하여 동기화 대상에 포함할 파일 종류와 위치를 정의한다.
- **Acceptance Criteria**:
  - [ ] Bash/Shell 스크립트: 저장소 루트 기준 `scripts/**/*.sh`, `bin/**/*.sh`, 기타 실행 비트가 켜진 `*.sh`
  - [ ] Makefile: 저장소 루트 및 1-depth 하위의 `Makefile`, `*.mk`
  - [ ] Django management commands: `**/management/commands/*.py` (단, `__init__.py` 제외)
  - [ ] Justfile, npm scripts(`package.json`의 `scripts` 필드)는 향후 확장 후보로 명시 (이번 범위 외)
  - [ ] 인식 규칙은 `references/script-sources.md` 같은 단일 레퍼런스 문서에 정의되어 모든 skill/agent가 참조한다
  - [ ] 카테고리 명칭은 `scripts/` 하위에서만 유효하다 — 루트 레벨 `django-commands/`(datamaker-docs 기존 구조)는 더 이상 인식 대상이 아니며, `scripts/django-command/`로 재분류된다

### FR-2: `sync-scripts` skill 추가

- **Description**: `sync-specs`와 동일한 워크플로로, 인식된 스크립트 파일을 저장소 외부기억의 `scripts/` 하위에 동기화하는 skill을 추가한다.
- **Acceptance Criteria**:
  - [ ] `skills/sync-scripts/` 경로에 SKILL.md가 존재한다
  - [ ] 현재 git repo를 자동 감지하고, 인식 규칙에 매칭되는 모든 스크립트를 수집한다
  - [ ] 저장 경로: `{directory}/{repo-name}/scripts/<카테고리>/<파일명>.md`
    - 카테고리: `bash`, `makefile`, `django-command` (확장 가능)
  - [ ] 원본 스크립트 코드는 Markdown fenced code block(`​```bash` / `​```makefile` / `​```python`)으로 보존한다
  - [ ] frontmatter에 `source_path`, `script_type`, `synced_at`, `repo`를 기록한다
  - [ ] 부분 동기화: `/sync-scripts <path-or-glob>` 인자가 주어지면 해당 범위만 동기화한다

### FR-3: 폴더 구조 확장

- **Description**: 저장소 외부기억 루트(`{directory}/{repo-name}/`) 아래에 `specs/`와 `ideas/`에 더해 `scripts/` 디렉토리를 둔다.
- **Acceptance Criteria**:
  - [ ] repo 초기화 단계에서 `scripts/` 디렉토리도 함께 생성한다 (`repo-memory` 에이전트)
  - [ ] obsidian 백엔드: `{vault}/{directory}/{repo-name}/scripts/<카테고리>/...` 구조
  - [ ] filesystem/git 백엔드: `{basePath}/{directory}/{repo-name}/scripts/<카테고리>/...` 구조
  - [ ] repo 인덱스 노트(`{repo-name}.md`)에 `scripts/` 섹션 링크가 추가된다
  - [ ] 루트-레벨 평면 카테고리 폴더(`django-commands/`, `bash/` 등)는 생성·인식하지 않는다 — 반드시 `{repo-name}/scripts/<카테고리>/` 하위로만 저장
  - [ ] datamaker-docs의 기존 `django-commands/` 트리는 본 작업의 마이그레이션 가이드(`docs` 또는 plans.md)에 명시된 절차로 `synapse-backend/scripts/django-command/`로 이전 가능해야 한다

### FR-4: 검색·조회 시 `specs` / `scripts` 구분

- **Description**: local-memory를 통한 검색·조회 시 사용자가 범위를 `specs` 또는 `scripts`로 지정하거나, 전체에서 통합 검색할 수 있어야 한다.
- **Acceptance Criteria**:
  - [ ] `repo-memory` 에이전트가 호출되는 모든 skill에서 `scope: specs | scripts | all` 개념을 지원한다
  - [ ] 백엔드별 SEARCH 연산(`obsidian search query="path:..."` / `find "{basePath}/.../scripts" ...`)이 해당 scope 경로에 한정되도록 분기한다
  - [ ] `/save-idea`처럼 별개 보관소(`ideas/`)는 영향을 받지 않는다

### FR-5: `check-settings` 확장

- **Description**: `/check-settings`가 신규 `scripts` 동기화 관련 환경/설정을 검증한다.
- **Acceptance Criteria**:
  - [ ] 저장소 외부기억 경로 아래에 `scripts/` 쓰기 권한 확인 (filesystem/git)
  - [ ] obsidian 백엔드의 경우 `{directory}/{repo-name}/scripts/` 경로 통신 확인
  - [ ] Django command 감지를 위해 현재 repo가 Django 프로젝트인지 가벼운 휴리스틱(예: `manage.py` 존재) 보고 — 미존재 시 정보성 메시지로만 안내

### FR-6: `repo-memory` 에이전트 분기 확장

- **Description**: `repo-memory` 에이전트의 사전 검사/폴더 초기화/링크 형식 처리에 `scripts/` 트리를 포함한다.
- **Acceptance Criteria**:
  - [ ] 폴더 초기화에서 `scripts/`와 카테고리 하위 폴더 생성
  - [ ] 인덱스 노트의 wikilinks / 표준 마크다운 링크에 `scripts/` 추가
  - [ ] `scope` 인자를 받아 백엔드별 명령으로 변환하는 책임을 가짐

### FR-7: specs / scripts 지시문 격리 (Agent 혼동 방지)

- **Description**: 사용자가 자연어로 "django command 동기화" / "스크립트 저장" 등을 요청할 때 에이전트가 `sync-specs` 흐름으로 잘못 라우팅하는 현상을 차단한다. specs 관련 지시와 scripts 관련 지시는 어휘·skill 파일·scope 키워드 수준에서 분리되어야 한다.
- **Acceptance Criteria**:
  - [ ] skill 파일 분리: `sync-specs/SKILL.md`와 `sync-scripts/SKILL.md`는 서로의 동작을 언급하지 않는다 (cross-reference 금지)
  - [ ] 어휘 분리: `sync-specs`는 "spec 문서 / requirements / specs / plans"만 다룬다. `sync-scripts`는 "스크립트 / bash / makefile / django command"만 다룬다. 동일 단락에서 두 영역의 트리거 단어를 혼합 사용 금지
  - [ ] scope 라우팅: `repo-memory(scope=specs|scripts|all)`로 호출 인자를 통해 분기하며, 에이전트는 사용자 의도가 모호할 때 어느 scope인지 명시적으로 확인 후 진행한다
  - [ ] 자연어 의도 매핑 가이드를 `references/script-sources.md` 또는 별도 레퍼런스에 두어 에이전트가 "django management command", "manage.py command", "shell 스크립트" 같은 사용자 표현을 모두 `scope=scripts`로 라우팅하도록 한다
  - [ ] 에이전트 사전 검사 출력 메시지에서 specs/scripts 영역을 시각적으로 구분(예: "[specs]" / "[scripts]" 라벨)

### FR-8: 플러그인 표면 텍스트의 백엔드 중립화

- **Description**: local-memory 플러그인은 `obsidian` / `filesystem` / `git` 세 백엔드를 동등하게 지원하지만, 현재 다수의 표면 텍스트(설명, 키워드, README, AGENT/SKILL/명령어 본문, 예시)가 여전히 Obsidian 사용을 전제하거나 우선시한다. 본 작업에서는 이 표현을 백엔드 중립으로 재정리하여, 사용자가 `datamaker-docs` 같은 git 저장소 백엔드를 1급으로 인지하도록 한다.
- **Acceptance Criteria**:
  - [ ] `plugin.json` `description`에서 백엔드 이름을 특정하지 않는다 (예: "선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리"). 키워드 순서/구성도 어느 한 백엔드에 치우치지 않게 조정 (`obsidian`, `vault`만 강조 금지)
  - [ ] `README.md` 헤드라인과 개요 단락에서 "Obsidian vault 또는 …" / "Obsidian이 없는 서버 환경에서도" 같은 위계적 표현 제거. 백엔드 3종을 대등하게 소개
  - [ ] README "Backend 설정" 예시 블록 순서·강조가 균등 (`obsidian`을 "기본값"으로 라벨링하지 않고 별도 주석으로 분리)
  - [ ] `README.md`의 vault 예시명(`MyVault`)을 일반화하거나, `datamaker-docs` 같은 실제 git 저장소 예시와 병기
  - [ ] `agents/repo-memory/AGENT.md`, `skills/*/SKILL.md`, `commands/check-settings.md`의 모든 본문에서 다음 정리:
    - 섹션 헤더 "Vault 설정 읽기" → "백엔드 설정 읽기"
    - description 필드의 "Obsidian vault 또는 로컬 파일시스템에" → "선택된 백엔드(obsidian / filesystem / git)에"
    - `vault-name` 변수명이 obsidian 외 백엔드 흐름 설명에 등장하지 않도록 한다 (백엔드별 분기 안에서만 등장)
    - 기본값 안내 문구에서 "(기본값: `obsidian`)" 같은 단일 백엔드 명시 표기를 제거하거나 별도 주석으로 분리
  - [ ] 기본 백엔드 정책 재검토: 후방호환을 위해 동작 수준의 기본값(`obsidian`)은 보존하더라도, 신규 사용자 흐름(`/check-settings`)에서는 백엔드를 명시적으로 선택하도록 유도 (기본값 무음 적용 금지)
  - [ ] 본 sync-scripts 관련 신규 문서(`sync-scripts/SKILL.md`, `script-sources.md`, 마이그레이션 가이드)는 처음부터 중립 어조로 작성

### FR-9: 기존 데이터 마이그레이션 전략 (Plugin Update)

- **Description**: 본 업데이트(v2.0.0 → v2.1.0)는 기존 사용자의 `.claude/local-memory.json` 및 외부기억 저장소(specs/, ideas/, repo 인덱스 노트)를 손상시키지 않아야 한다. 신규 `scripts/` 구조와 FR-7/FR-8 변경이 기존 데이터에 미치는 영향을 사전에 정의하고, 안전한 진입 경로를 보장한다.
- **Acceptance Criteria**:
  - [ ] **설정 호환**: v2.0.0에서 작성된 `.claude/local-memory.json`이 변경 없이 v2.1.0에서 동작한다. 신규 필드는 모두 선택이며 미지정 시 기존 동작 유지
  - [ ] **기존 트리 무손상**: 업그레이드 행위 자체가 `{directory}/{repo-name}/specs/`, `{directory}/{repo-name}/ideas/`, `{directory}/{repo-name}/{repo-name}.md` 등 기존 파일을 변경하지 않는다 — 모든 쓰기는 사용자가 skill을 명시 호출한 시점에만 발생
  - [ ] **scripts/ Lazy-create**: 신규 `{directory}/{repo-name}/scripts/<카테고리>/` 트리는 `/sync-scripts` 또는 `repo-memory(scope=scripts|all)`가 최초 호출되는 시점에만 생성한다. `/sync-specs`나 `/save-idea` 단독 사용 시에는 생성하지 않는다
  - [ ] **인덱스 노트 비파괴 병합**: 기존 `{repo-name}.md` 인덱스에 `## Scripts` 섹션이 없으면, `repo-memory`가 `scope=scripts|all` 컨텍스트에서 노트를 읽어 `## Ideas` 섹션 직전(또는 본문 끝)에 `## Scripts` 블록만 append 한다. 사용자가 직접 추가한 다른 섹션·문구는 보존
  - [ ] **인덱스 노트 부재 시**: 인덱스 노트가 아예 없으면 신규 템플릿(specs / scripts / ideas 모두 포함)으로 생성한다 — 기존 동작(specs/ideas만 포함)에서 자연스럽게 상위 호환
  - [ ] **/check-settings 마이그레이션 감사**: `/check-settings` 출력에 신규 절(`### 마이그레이션 감사`)이 추가되어 다음을 보고한다 — 인덱스 노트 존재/`## Scripts` 섹션 존재/`scripts/` 디렉토리 존재 여부, 그리고 누락 시 어떤 명령으로 보강 가능한지 안내
  - [ ] **idempotency**: 업그레이드 후 `/sync-specs`, `/save-idea`를 재실행해도 기존 파일을 중복 생성하지 않고 v2.0.0과 동일한 결과를 만든다 (frontmatter `synced` 필드만 갱신)
  - [ ] **README 업그레이드 노트**: README에 "v2.0.0에서 v2.1.0으로 업그레이드" 절이 추가되어, 위 보장 사항·신규 기능 진입 경로·필요 시 마이그레이션 명령을 요약 제시
  - [ ] **datamaker-docs 분리 명시**: datamaker-docs의 루트 평면 `django-commands/` 트리는 본 FR-9의 자동 마이그레이션 대상이 아니며, Step 9의 사용자 수동 가이드(`docs/migrations/datamaker-docs-django-commands.md`)에 의해서만 이전됨을 본 FR 본문과 README 업그레이드 노트에 명시
  - [ ] **롤백 안전성**: v2.1.0 산출물(특히 인덱스 노트의 신규 `## Scripts` 섹션)은 v2.0.0에서 읽어도 단순 마크다운으로 무해함을 명시 (downgrade 시 에러 없음)

## Non-Functional Requirements

- **호환성**: 기존 `sync-specs`, `save-idea`, `/check-settings` 동작에 회귀가 없어야 한다
- **단순성**: 스크립트 인식 규칙은 단일 레퍼런스 문서에 두고, 모든 skill/agent가 동일 규칙을 따른다
- **이식성**: macOS/Linux 모두에서 동작해야 하며 Python/Django는 선택적이다 (`manage.py` 없을 때 무시)
- **이중관리 방지**: 동기화된 외부기억은 read-only 사본으로 다룬다 — 외부기억 쪽 수정은 다음 sync 시 덮어쓴다

## Constraints

- 이 플러그인은 마크다운 기반 spec 파일로 동작 로직이 기술되므로, 코드 실행 없이 백엔드 명령 매핑을 텍스트로 분기한다
- 스크립트 본문은 그대로 보존되어야 하며 임의 변형(formatter, lint) 금지
- 거대한 스크립트 트리에서도 안전하도록 기본 동작은 "변경된 파일만 sync"가 아닌 "전체 덮어쓰기" — 단순성 우선

## Out of Scope

- Justfile, `package.json` scripts, GitHub Actions YAML 등 추가 스크립트 형식 지원 (향후)
- 스크립트 실행/오케스트레이션 기능 (local-memory는 저장·검색만 담당)
- 스크립트 변경 감지 hook 자동화 (`/sync-scripts` 수동 호출만 제공)
- 외부기억 → 원본 역방향 동기화

## References

- [requirements.md (create-local-memory-plugin)](../create-local-memory-plugin/requirements.md)
- [requirements.md (abstraction-for-local-memory-plugin)](../abstraction-for-local-memory-plugin/requirements.md)
- [backend-operations.md](../../plugins/local-memory/references/backend-operations.md)
- [sync-specs SKILL.md](../../plugins/local-memory/skills/sync-specs/SKILL.md)
- [repo-memory AGENT.md](../../plugins/local-memory/agents/repo-memory/AGENT.md)
- `/Users/jongtaek.hwang/Projects/datamaker-docs/README.md` — 실제 local-memory 운영 구조
- `/Users/jongtaek.hwang/Projects/datamaker-docs/django-commands/` — 재분류 대상 레거시 트리
- `/Users/jongtaek.hwang/Projects/datamaker-docs/specs/synapse-backend/` — repo-scoped specs 운영 예시
