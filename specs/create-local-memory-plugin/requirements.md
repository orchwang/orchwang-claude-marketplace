# Requirements: Create local-memory plugin

> Created: 2026-03-07
> Status: Draft
> Ticket: N/A

## Overview

Claude Code가 작업 중 생성하는 컨텍스트(requirements, specs, plans, 아이디어 메모 등)를 Obsidian vault에 외부기억으로 저장·관리하기 위한 플러그인이다. Obsidian vault와의 상호작용은 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) 플러그인이 제공하는 `obsidian-cli`, `obsidian-markdown` skill에 의존하며, 본 플러그인은 그 위에 GitHub repo 단위 컨텍스트 분류·관리 계층을 추가한다.

## Goals

- [ ] kepano/obsidian-skills 플러그인을 의존성으로 설정
- [ ] GitHub repo 기준으로 컨텍스트를 분류·저장하는 repo-memory agent 구현
- [ ] specs 문서(requirements, specs, plans)를 Obsidian에 동기화하는 skill 구현
- [ ] 아이디어 메모를 idea 항목으로 저장·활용하는 skill 구현

## Functional Requirements

### FR-1: obsidian-skills 의존성

- **Description**: Obsidian vault와의 상호작용은 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) 플러그인에 위임한다. 이 플러그인이 제공하는 5개 skill을 활용한다. Obsidian CLI는 Obsidian 앱에 내장된 기능이며(별도 패키지 아님), 앱이 실행 중이어야 동작한다.
- **Acceptance Criteria**:
  - [ ] plugin.json에 `kepano/obsidian-skills`를 의존성으로 명시한다
  - [ ] obsidian-skills 플러그인 미설치 시 사용자에게 설치 안내를 제공한다
  - [ ] Obsidian 앱 설치 여부 및 CLI 지원 버전인지 사전 검사를 수행한다
  - [ ] Obsidian 앱 미실행 시 실행을 안내한다
- **활용하는 obsidian-skills 제공 skill**:
  - `obsidian:obsidian-cli` — vault CRUD, 검색, 태그, 속성 관리 (`obsidian create/read/append/search/property:set/tags` 등)
  - `obsidian:obsidian-markdown` — Obsidian Flavored Markdown 작성 (wikilinks, embeds, callouts, frontmatter)
  - `obsidian:obsidian-bases` — .base 파일 데이터베이스 뷰 (향후 활용 가능)
  - `obsidian:json-canvas` — .canvas 시각적 캔버스 (향후 활용 가능)
  - `obsidian:defuddle` — 웹페이지 클린 마크다운 추출 (향후 활용 가능)

### FR-2: repo-memory 에이전트

- **Description**: GitHub repo 단위로 외부기억을 관리하는 에이전트를 추가한다. 현재 작업 중인 repo name을 기준으로 컨텍스트를 분류하여 Obsidian vault에 저장한다.
- **Acceptance Criteria**:
  - [ ] `agents/repo-memory/` 경로에 에이전트 playbook이 존재한다
  - [ ] 현재 git repo name을 자동으로 감지할 수 있다
  - [ ] repo name을 기준으로 vault 내 폴더를 구조화한다

### FR-3: specs 동기화 skill

- **Description**: `specs/{task-name}/` 하위의 requirements.md, specs.md, plans.md 등 SDD 문서를 Obsidian vault에 동기화하는 skill을 추가한다. 컨텍스트(task) 별로 구분되어 기록되어야 한다.
- **Acceptance Criteria**:
  - [ ] `skills/sync-specs/` 경로에 skill이 존재한다
  - [ ] specs 디렉토리의 requirements.md, specs.md, plans.md를 Obsidian vault에 저장한다
  - [ ] vault 내 저장 경로는 `{repo-name}/{task-name}/` 구조를 따른다
  - [ ] 문서 변경 시 vault의 해당 노트도 업데이트된다
  - [ ] 각 문서의 메타데이터(생성일, 상태 등)가 Obsidian frontmatter로 보존된다

### FR-4: 아이디어 메모 skill

- **Description**: GitHub repo 작업 중 발생하는 아이디어, 메모 등을 idea 항목으로 Obsidian vault에 저장하고 활용할 수 있는 skill을 추가한다.
- **Acceptance Criteria**:
  - [ ] `skills/save-idea/` 경로에 skill이 존재한다
  - [ ] 아이디어 메모를 vault의 `{repo-name}/ideas/` 하위에 저장한다
  - [ ] 아이디어에 제목, 내용, 태그, 생성일이 포함된다
  - [ ] 저장된 아이디어 목록을 조회할 수 있다

## Non-Functional Requirements

- **Performance**: Obsidian CLI 명령 호출은 단일 작업당 2초 이내에 완료되어야 한다
- **Security**: vault 경로 외부에 파일을 생성하거나 수정하지 않아야 한다
- **Scalability**: repo 수 및 노트 수가 증가해도 폴더 구조 기반으로 관리가 가능해야 한다

## Constraints

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) 플러그인이 Claude Code에 설치되어 있어야 한다
- Obsidian 앱(v1.12+)이 설치되어 있어야 한다 — CLI는 앱에 내장된 기능 (별도 설치 불필요)
- Obsidian 앱이 실행 중이어야 한다 — CLI는 실행 중인 Obsidian 인스턴스와 통신
- Obsidian 인스톨러가 최신이어야 CLI 기능이 완전히 지원됨 (구버전 인스톨러 경고 존재)
- 플러그인 구조는 기존 `plugins/orchwang-general/` 패턴을 따른다 (plugin.json, agents/, skills/, commands/)

## Out of Scope

- Obsidian 클라우드 동기화 (Obsidian Sync 등)
- 원격 vault 지원 (로컬 vault만 대상)
- Obsidian vault CRUD 직접 구현 (obsidian-skills에 위임)
- 다른 노트 앱(Notion, Bear 등) 지원

## References

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Obsidian vault 상호작용 의존성
- [Obsidian CLI 문서](https://help.obsidian.md/cli)
- [Obsidian Frontmatter 문서](https://help.obsidian.md/Editing+and+formatting/Properties)
- 기존 플러그인 구조: `plugins/orchwang-general/plugin.json`
- SDD Helper workflow: `/sdd-helper:specify-with-requirements`
