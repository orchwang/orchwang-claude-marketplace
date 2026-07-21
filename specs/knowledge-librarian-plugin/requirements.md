# Requirements: knowledge-librarian plugin

> Created: 2026-07-21
> Updated: 2026-07-21
> Status: Draft
> Ticket: N/A

## Overview

`local-memory` 플러그인은 Claude Code 작업 중 *생성되는* 산출물(specs · scripts · ideas)을 `{repo-name}/` 단위로 외부 저장소에 **밀어내는(write-out)** 외부기억 도구다. 데이터의 소유자는 현재 repo이고, 방향은 바깥을 향한다.

이번 작업은 성격이 반대인 요구를 다룬다: 사람이 별도로 관리하는 **wiki/지식 저장소(md 문서 모음)를 지정**하고, 그 안의 특정 위치에 있는 문서를 Claude Code 작업의 **근거 지식으로 읽어 들이는(read-in)** 기능이다. 나아가 이 지식을 탐색하는 **indexer 서브에이전트**가 관련 문서를 찾아 다른 전문 서브에이전트(예: `data-engineer`, `ontology-expert`)에게 근거로 **전달(dispatch)** 할 수 있어야 한다.

두 기능은 데이터 방향(write vs read), 소스 소유권(repo 생성물 vs 사람이 관리하는 wiki), 스코프(`{repo-name}` vs 도메인/토픽), 핵심 역할(기록 vs 탐색+전달)이 모두 다르다. 또한 wiki는 **read-only source of truth**로 취급되어 플러그인이 실수로 덮어써서는 안 된다. 따라서 본 기능은 `local-memory`에 얹지 않고 **`knowledge-librarian`이라는 별도 플러그인**으로 신설한다. 단 backend 추상화(obsidian / filesystem / git), `.claude/*.json` 전용 설정 패턴, agent + skill + references 구조는 `local-memory`에서 검증된 방식을 재사용한다.

### Reference: local-memory와의 대비

| 축 | local-memory | knowledge-librarian |
|---|---|---|
| 데이터 방향 | 작업 산출물을 밖으로 **write** | 큐레이션된 지식을 안으로 **read** |
| 소스 소유권 | Claude/repo가 생성 | 사람이 별도 관리하는 wiki (read-only) |
| 스코프 | `{repo-name}/` 단위 | 도메인/토픽 단위, 여러 repo가 공유 |
| 핵심 역할 | 기록(capture) | 탐색(index) + 전문가 전달(dispatch) |
| 설정 파일 | `.claude/local-memory.json` | `.claude/knowledge-librarian.json` (분리) |
| 공유 자산 | backend 추상화, 전용 설정, agent/skill 구조 | 동일 방식을 재사용 |

## Goals

- [ ] wiki/지식 저장소(git repo 또는 로컬 디렉토리)를 지식 소스로 지정하고, 그 안의 특정 위치(roots)만 지식 대상으로 한정한다
- [ ] 지정된 소스의 md 문서를 스캔하여 경량 카탈로그(인덱스)를 생성·갱신한다
- [ ] 자연어 질의로 카탈로그를 검색하고 랭킹된 발췌를 반환한다
- [ ] indexer 에이전트가 관련 지식을 모아 다른 전문 서브에이전트에게 근거로 전달(dispatch)한다
- [ ] 지식 소스는 절대 변경하지 않는다(read-only 보장) — 인덱스는 현재 repo 또는 지정 경로에만 저장한다
- [ ] 기존 backend 3종(obsidian / filesystem / git)에서 동작한다 (git/filesystem이 1급, obsidian은 vault 소스 지원)
- [ ] 다중 지식 소스를 지원한다
- [ ] `local-memory`와 설정·명령·scope가 충돌하지 않는다

## Functional Requirements

### FR-1: 지식 소스 지정

- **Description**: wiki/지식 저장소와 그 안의 지식 위치를 설정으로 지정한다.
- **Acceptance Criteria**:
  - [ ] `.claude/knowledge-librarian.json`의 `sources[]` 배열에 하나 이상의 소스를 정의한다
  - [ ] 각 소스는 `name`(식별자), `backend`(또는 전역 `backend` 상속), 위치(`basePath` for filesystem/git · `vault` for obsidian), `roots[]`(소스 루트 기준 상대경로 목록)를 가진다
  - [ ] `roots[]`가 지정되면 그 하위만 지식 대상으로 한정한다. 비면 소스 전체를 대상으로 한다
  - [ ] `include[]` / `exclude[]` 글롭으로 파일을 필터링한다 (기본 `include`: `**/*.md`)
  - [ ] 존재하지 않는 `basePath`/`root`는 pre-flight에서 명확한 오류로 안내한다

### FR-2: 지식 카탈로그 인덱싱

- **Description**: 지정된 소스의 md 문서를 스캔하여 경량 카탈로그를 만든다. 문서 본문 전체가 아니라 검색에 필요한 메타데이터만 담는다.
- **Acceptance Criteria**:
  - [ ] 각 카탈로그 엔트리는 `source`(소스 name), `path`(소스 루트 기준 상대경로), `title`(첫 H1 또는 frontmatter `title` 또는 파일명), `headings[]`(H2/H3 목록), `tags[]`(frontmatter tags), `categories[]`/`series`(있을 때), `summary`(frontmatter `summary`/`description`/`excerpt` 또는 첫 문단), `size`, `mtime`를 가진다
  - [ ] frontmatter가 있으면 파싱하여 `title` / `tags` / `categories` / `series` / `summary`에 우선 반영한다. `summary`는 `summary` > `description` > `excerpt`(Jekyll) 순으로 취한다
  - [ ] frontmatter `published: false`(Jekyll 초안)인 문서는 인덱싱에서 제외한다
  - [ ] 인덱스는 소스 저장소가 아니라 `indexPath`(기본 `.claude/knowledge-index.json`)에 저장한다 — **소스는 쓰지 않는다**
  - [ ] 재인덱싱은 `mtime`/`size` 비교로 변경분만 갱신하며, `--force`로 전체 재구축한다
  - [ ] 인덱스에 `generatedAt`, 소스별 문서 수를 기록한다

### FR-3: scope 검색

- **Description**: 자연어 질의로 카탈로그를 검색하여 관련 문서와 발췌를 반환한다.
- **Acceptance Criteria**:
  - [ ] 질의 토큰을 `title` / `headings` / `tags` / `summary`에 대해 매칭하여 랭킹한다 (title·heading·tag 가중치 우위)
  - [ ] `--source <name>`으로 특정 소스로 검색을 한정한다
  - [ ] `--limit N`(기본 5)으로 반환 개수를 제한한다
  - [ ] 각 결과는 `path`, `title`, 관련 heading, 매칭 근거 발췌를 포함한다
  - [ ] 인덱스가 없거나 staleness가 감지되면 먼저 `/knowledge-index`를 안내한다

### FR-4: 전문가 서브에이전트 디스패치 (indexer → specialist)

- **Description**: librarian이 질문에 관련된 지식을 모아 다른 전문 서브에이전트에게 근거로 첨부해 위임한다. 본 플러그인의 핵심 차별점이다.
- **Acceptance Criteria**:
  - [ ] `/knowledge-ask "질문" [--to <agent>] [--source <name>]` 형태로 호출한다
  - [ ] librarian은 (1) 검색(FR-3)으로 관련 문서를 선별하고 (2) 필요한 발췌를 소스에서 READ하여 (3) `--to`로 지정된 서브에이전트를 Agent 도구로 호출하며 발췌를 근거 컨텍스트로 전달한다
  - [ ] `--to` 미지정 시 질문 성격에 맞는 후보 에이전트를 `AskUserQuestion`으로 제시하고, 무음 기본값을 적용하지 않는다
  - [ ] 대상 에이전트는 마켓플레이스에 실재하는 에이전트(예: `data-engineer`, `ontology-expert`, `general-purpose`) 중에서 선택한다 — 미존재 에이전트 지정 시 오류 안내
  - [ ] 전달되는 근거에는 각 발췌의 출처(`source`, `path`)를 명시하여 전문가가 인용할 수 있게 한다

### FR-5: Read-only 안전성

- **Description**: 지식 소스는 절대 변경하지 않는다.
- **Acceptance Criteria**:
  - [ ] 플러그인의 어떤 skill/agent도 소스(`basePath`/`vault`) 하위에 파일을 생성·수정·삭제하지 않는다
  - [ ] git 소스에 대해 commit/push를 수행하지 않는다 (local-memory의 git 백엔드 write 동작과 명확히 구분)
  - [ ] 소스별 `readOnly`는 항상 참으로 간주하며, 설정에 명시하지 않아도 변경 금지가 기본이다
  - [ ] 인덱스·캐시 등 플러그인 산출물은 현재 repo의 `.claude/` 또는 `indexPath`에만 기록한다

### FR-6: Backend 추상화 재사용

- **Description**: `local-memory`의 backend 추상화(obsidian / filesystem / git)를 재사용하되 read 경로만 사용한다.
- **Acceptance Criteria**:
  - [ ] filesystem / git: `find` + `cat`(READ)로 스캔·읽기. git 소스라도 read-only이므로 checkout/commit 없이 워킹트리를 그대로 읽는다
  - [ ] obsidian: `obsidian vault=... search`/`read`로 스캔·읽기
  - [ ] 백엔드별 READ/SEARCH/EXISTS 명령 매핑을 단일 레퍼런스로 문서화한다
  - [ ] `backend` 미설정 시의 기본값·안내는 `local-memory` 관례와 정합한다

### FR-7: 다중 소스 지원

- **Description**: 여러 wiki/지식 저장소를 동시에 지식 소스로 둘 수 있다.
- **Acceptance Criteria**:
  - [ ] `sources[]`에 2개 이상 정의 가능하며, 인덱스는 `source` 필드로 구분한다
  - [ ] 검색·디스패치는 전체 소스 통합 또는 `--source`로 특정 소스 한정을 지원한다
  - [ ] 소스별 `backend`를 개별 지정할 수 있고, 미지정 시 전역 `backend`를 상속한다

### FR-8: 인덱스 최신성(staleness) 관리

- **Description**: 소스가 변경되었는데 인덱스가 오래된 경우를 감지·안내한다.
- **Acceptance Criteria**:
  - [ ] 검색·디스패치 시 인덱스의 `generatedAt`과 소스 파일 `mtime`을 비교하여 stale 여부를 판단한다
  - [ ] stale 감지 시 결과를 반환하되 "인덱스가 오래되었을 수 있음 — `/knowledge-index` 권장" 경고를 병기한다
  - [ ] 인덱스 자체가 없으면 검색을 중단하고 `/knowledge-index`를 먼저 안내한다

### FR-9: 설정 검토 명령

- **Description**: 설정을 대화형으로 점검·보완한다 (`local-memory`의 `/check-settings`에 대응).
- **Acceptance Criteria**:
  - [ ] `/knowledge-settings` 실행 시 `.claude/knowledge-librarian.json` 존재·필수 항목·소스 접근성을 점검한다
  - [ ] 누락 항목은 `AskUserQuestion`으로 대화형 보완하고 결과를 설정 파일에 저장한다
  - [ ] 각 소스의 `basePath`/`vault` 접근성과 `roots` 존재를 검사하여 보고한다

### FR-10: local-memory와의 공존·경계

- **Description**: 두 플러그인이 동시에 설치되어도 설정·명령·scope가 충돌하지 않는다.
- **Acceptance Criteria**:
  - [ ] 설정 파일(`.claude/knowledge-librarian.json`)은 `local-memory.json`과 완전히 분리한다
  - [ ] 명령/스킬 이름은 `knowledge-*` 접두를 사용하여 `sync-*` 계열과 어휘·트리거가 겹치지 않는다
  - [ ] README에 두 플러그인의 역할 차이(write-out vs read-in)를 명시한다
  - [ ] 선택적 상호운용: `local-memory`가 저장한 `{repo}/specs/` 트리를 knowledge 소스로도 지정 가능함을 문서화한다 (강제 아님)

## Non-Functional Requirements

- **문서 언어**: 한국어 (AGENTS.md 규칙)
- **파일 규칙**: kebab-case 폴더/명령명, 2-space YAML 들여쓰기
- **패키징**: `plugin.json` + `README.md` 필수 (AGENTS.md "Plugin Documentation Requirements")
- **무침습**: 소스 저장소 및 사용자의 기존 `local-memory` 데이터를 건드리지 않는다
- **외부 의존성**: 신규 런타임 의존성 추가 없음 (마크다운 spec 기반 동작). obsidian 소스 사용 시에만 obsidian 플러그인 의존

## Out of Scope

- 임베딩/벡터 검색 기반 시맨틱 랭킹 (이번엔 키워드/헤딩/태그 랭킹만; 향후 확장 후보)
- 소스 저장소에 대한 쓰기·편집·PR 생성
- md 이외 포맷(PDF, docx, Confluence API 등) 인덱싱 (향후 확장 후보)
- 실시간 파일 변경 감시(watch) — 명시적 `/knowledge-index` 호출로 갱신
