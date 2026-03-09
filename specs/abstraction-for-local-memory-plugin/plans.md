# Plans: Abstraction for local-memory plugin

> Created: 2026-03-09
> Status: Complete
> Specs: [specs.md](./specs.md)

## Overview

6단계로 구현을 진행한다. 먼저 중앙 레퍼런스 문서를 생성하고, 에이전트/명령어/스킬을 순서대로 업데이트한 후, 마지막으로 메타데이터와 문서를 갱신한다.

## Implementation Steps

### Step 1: `references/backend-operations.md` 생성

- 4가지 연산(CREATE, READ, SEARCH, EXISTS)을 백엔드별로 정의
- Pre-flight check 절차를 백엔드별로 명시
- 링크 형식 가이드 포함

### Step 2: `agents/repo-memory/AGENT.md` 업데이트

- `backend` 설정 읽기 로직 추가
- Pre-flight check를 백엔드별로 분기
- 폴더 구조 초기화에서 wikilinks vs 표준 링크 분기
- 설정 항목 문서 갱신

### Step 3: `commands/check-settings.md` 업데이트

- Step 1 환경 검사를 백엔드별로 분기
- Step 2 설정 검토에 `backend`, `basePath` 추가
- Step 5 연결 테스트를 백엔드별로 분기

### Step 4: `skills/sync-specs/SKILL.md` 업데이트

- Step 3 저장 명령을 백엔드별로 분기
- git 백엔드: 모든 파일 쓰기 후 단일 커밋+push

### Step 5: `skills/save-idea/SKILL.md` 업데이트

- Step 5 중복 확인을 백엔드별로 분기
- Step 6 저장 명령을 백엔드별로 분기
- 목록 조회를 백엔드별로 분기

### Step 6: `plugin.json` 및 `README.md` 업데이트

- 버전 2.0.0으로 업데이트
- 설명 변경: "Obsidian vault 또는 로컬 파일시스템에 저장·관리"
- `"filesystem"` 키워드 추가
- README에 Backend Configuration 섹션 추가

## Task Breakdown

| # | Task | 파일 | 상태 |
|---|------|------|------|
| 1 | backend-operations.md 생성 | `references/backend-operations.md` | Done |
| 2 | AGENT.md 업데이트 | `agents/repo-memory/AGENT.md` | Done |
| 3 | check-settings.md 업데이트 | `commands/check-settings.md` | Done |
| 4 | sync-specs SKILL.md 업데이트 | `skills/sync-specs/SKILL.md` | Done |
| 5 | save-idea SKILL.md 업데이트 | `skills/save-idea/SKILL.md` | Done |
| 6 | plugin.json + README.md 업데이트 | `plugin.json`, `README.md` | Done |

## Testing Strategy

1. 플러그인 재설치: `/plugin install local-memory@orchwang-marketplace`
2. `/check-settings` 실행 — 백엔드 감지 및 검증 확인
3. `backend: "filesystem"` + 테스트 basePath로 `/save-idea "test"` — 파일 생성 확인
4. `backend: "obsidian"`으로 `/sync-specs` — 기존 동작 확인
5. `backend: "git"`으로 `/save-idea "test"` — 파일 생성 및 git commit 확인

## Rollback Plan

- `plugin.json` 버전을 1.1.0으로 되돌림
- 각 파일을 이전 커밋에서 복원 (`git checkout HEAD~1 -- <file>`)
- `references/` 디렉토리 삭제

## Progress Tracking

| Step | Status | Notes |
|------|--------|-------|
| Step 1: backend-operations.md | Done | 레퍼런스 문서 생성 완료 |
| Step 2: AGENT.md | Done | 백엔드별 Pre-flight, 폴더 초기화 분기 |
| Step 3: check-settings.md | Done | 백엔드별 환경 검사, 연결 테스트 분기 |
| Step 4: sync-specs SKILL.md | Done | 백엔드별 저장, git 배치 커밋 |
| Step 5: save-idea SKILL.md | Done | 백엔드별 저장/검색/목록 분기 |
| Step 6: plugin.json + README | Done | v2.0.0, 키워드, Backend Configuration |
