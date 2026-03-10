# Requirements: Abstraction for local-memory plugin

> Created: 2026-03-09
> Status: Draft
> Ticket: N/A

## Overview

local-memory 플러그인은 현재 Obsidian CLI(`kepano/obsidian-skills`)에 전적으로 의존하여 마크다운 파일을 저장한다. Ubuntu 서버 및 headless 환경에서는 Obsidian을 실행할 수 없으므로, 스토리지 백엔드를 추상화하여 설정으로 선택 가능하게 한다: `obsidian` (기존), `filesystem`, `git`.

모든 Obsidian CLI 사용은 YAML frontmatter가 포함된 마크다운 파일의 저장/읽기/검색으로 귀결되며, 파일시스템 작업으로 완전히 대체 가능하다.

## Goals

- [x] 스토리지 백엔드 추상화 (obsidian / filesystem / git)
- [x] 기존 obsidian 백엔드 동작 완전 호환 유지
- [x] Obsidian 없는 환경(서버, headless)에서 filesystem/git 백엔드로 사용 가능
- [x] git 백엔드를 통한 원격 저장소 자동 동기화

## Functional Requirements

### FR-1: Config Schema 확장

- **Description**: `.claude/local-memory.json`에 `backend`, `basePath`, `gitAutoCommit`, `gitRemote` 필드를 추가한다.
- **Acceptance Criteria**:
  - [x] `backend` 필드: `"obsidian"` (기본값) | `"filesystem"` | `"git"`
  - [x] `basePath` 필드: filesystem/git 백엔드에서 필수, 절대 경로
  - [x] `gitAutoCommit` 필드: git 백엔드 자동 커밋 여부 (기본값: `true`)
  - [x] `gitRemote` 필드: git 백엔드 push 대상 remote (기본값: `"origin"`)
  - [x] `backend` 미설정 시 기존 동작(`obsidian`) 유지

### FR-2: Backend Operations Reference

- **Description**: 4가지 핵심 연산(CREATE, READ, SEARCH, EXISTS)을 백엔드별로 정의하는 중앙 레퍼런스 문서를 생성한다.
- **Acceptance Criteria**:
  - [x] `references/backend-operations.md` 파일 생성
  - [x] obsidian / filesystem / git 별 명령어 매핑 정의
  - [x] git 백엔드의 커밋+push 정책 명시 (배치 커밋)

### FR-3: 백엔드별 Pre-flight Check

- **Description**: repo-memory 에이전트의 사전 검사를 백엔드에 따라 분기한다.
- **Acceptance Criteria**:
  - [x] obsidian: 기존 검사 유지 (앱 설치, CLI, vault 통신)
  - [x] filesystem: basePath 존재 및 쓰기 권한 확인
  - [x] git: filesystem 검사 + git 저장소 여부 확인

### FR-4: check-settings 백엔드 지원

- **Description**: `/check-settings` 명령어가 백엔드를 인식하고 적절한 검사를 수행한다.
- **Acceptance Criteria**:
  - [x] 백엔드별 환경 검사 항목 분기
  - [x] 백엔드별 필수 설정 항목 검증 (vault vs basePath)
  - [x] 연결 테스트: filesystem/git는 write+read+delete 테스트 파일 사용

### FR-5: sync-specs 백엔드 지원

- **Description**: `/sync-specs` skill이 백엔드에 따라 적절한 저장 명령을 사용한다.
- **Acceptance Criteria**:
  - [x] obsidian: 기존 `obsidian create` 명령 유지
  - [x] filesystem: `mkdir -p` + `cat >` 으로 파일 생성
  - [x] git: filesystem과 동일 + 모든 파일 쓰기 후 단일 커밋+push

### FR-6: save-idea 백엔드 지원

- **Description**: `/save-idea` skill이 백엔드에 따라 적절한 저장/검색 명령을 사용한다.
- **Acceptance Criteria**:
  - [x] 중복 확인: obsidian search vs `test -f`
  - [x] 저장: obsidian create vs `cat >`
  - [x] 목록 조회: obsidian search vs `ls`

### FR-7: 링크 형식 분기

- **Description**: filesystem/git 백엔드에서는 Obsidian wikilinks 대신 표준 마크다운 링크를 사용한다.
- **Acceptance Criteria**:
  - [x] obsidian: `![[path]]` wikilinks 사용
  - [x] filesystem/git: `[name](path/name.md)` 표준 링크 사용

## Non-Functional Requirements

- **호환성**: `backend` 미설정 시 기존 obsidian 동작과 100% 동일해야 한다
- **이식성**: filesystem/git 백엔드는 macOS, Linux 모두 지원해야 한다
- **단순성**: 백엔드 추가로 인한 복잡도 증가를 최소화한다

## Constraints

- 플러그인은 마크다운 기반 spec 파일이므로 코드 로직 없이 조건 분기를 텍스트로 기술한다
- Obsidian CLI 의존성은 obsidian 백엔드에서만 필요하다

## Out of Scope

- S3, Google Drive 등 클라우드 스토리지 백엔드
- 백엔드 간 마이그레이션 도구
- 동시 다중 백엔드 사용

## References

- [backend-operations.md](../../plugins/local-memory/references/backend-operations.md) — 백엔드별 명령어 레퍼런스
- [AGENT.md](../../plugins/local-memory/agents/repo-memory/AGENT.md) — repo-memory 에이전트
- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Obsidian CLI 플러그인
