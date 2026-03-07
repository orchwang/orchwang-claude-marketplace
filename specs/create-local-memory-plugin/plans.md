# Plans: Create local-memory plugin

> Created: 2026-03-07
> Updated: 2026-03-07
> Status: Ready
> Requirements: [requirements.md](./requirements.md)
> Specs: [specs.md](./specs.md)

## Overview

`local-memory` 플러그인을 `plugins/local-memory/` 경로에 생성한다. `kepano/obsidian-skills`에 의존하여 Obsidian vault CRUD를 수행하며, repo-memory 에이전트와 2개 skill(sync-specs, save-idea)을 구현한다.

## Prerequisites

- Obsidian 앱 설치 및 실행 (v1.12+, 최신 인스톨러 권장)
- `kepano/obsidian-skills` Claude Code 플러그인 설치 완료
- `obsidian help` 명령 정상 동작 확인

## Implementation Steps

### Step 1: 플러그인 스캐폴딩

- **Goal**: `local-memory` 플러그인의 디렉토리 구조와 매니페스트 생성
- **Specs Reference**: TS-1
- **Files**:
  - `plugins/local-memory/plugin.json` - Create - 플러그인 매니페스트 (의존성 포함)
  - `plugins/local-memory/README.md` - Create - 플러그인 설명 문서
  - `plugins/local-memory/agents/` - Create - 에이전트 디렉토리
  - `plugins/local-memory/skills/` - Create - skill 디렉토리
  - `plugins/local-memory/commands/` - Create - commands 디렉토리
- **Details**:
  - `plugin.json`에 `dependencies: ["kepano/obsidian-skills"]` 명시
  - `skills`에 `sync-specs`, `save-idea` 등록
  - `agents`에 `repo-memory` 등록
- **Validation**:
  - `plugins/local-memory/plugin.json`이 유효한 JSON이며 필수 필드 포함
- **Complexity**: Simple

### Step 2: repo-memory 에이전트

- **Goal**: repo 컨텍스트 관리 에이전트 playbook 작성
- **Specs Reference**: TS-2, TS-5, TS-6
- **Files**:
  - `plugins/local-memory/agents/repo-memory/AGENT.md` - Create - 에이전트 playbook
- **Details**:
  - Pre-flight check 로직 포함 (Obsidian 앱 설치/실행 확인, vault 통신 확인)
  - `.claude/settings.local.json`에서 vault 이름 읽기 (미설정 시 사용자에게 질문 후 `local-memory.vault`에 저장)
  - repo name 추출 로직 (`git remote get-url origin` → fallback: 디렉토리명)
  - vault 내 `{repo-name}/` 폴더 구조 생성 지시
  - 모든 `obsidian` CLI 호출에 `vault="{name}"` 파라미터 전달
  - 하위 skill 조율 역할 정의
- **Validation**:
  - AGENT.md가 Claude Code 에이전트 playbook 형식을 준수
  - Pre-flight check 단계별 실패 시 안내 메시지가 명확
- **Complexity**: Medium

### Step 3: sync-specs skill

- **Goal**: specs 문서를 Obsidian vault에 동기화하는 skill 구현
- **Specs Reference**: TS-3
- **Files**:
  - `plugins/local-memory/skills/sync-specs/SKILL.md` - Create - skill 정의
- **Details**:
  - `specs/` 디렉토리 스캔하여 task 목록 수집
  - 각 task의 requirements.md, specs.md, plans.md를 읽음
  - Obsidian frontmatter 생성 (source, repo, task, type, status, synced, tags)
  - `obsidian create ... overwrite silent` 명령으로 vault에 저장
  - 인자 없이 실행 시 전체 동기화, task-name 지정 시 해당 task만 동기화
- **Validation**:
  - `/sync-specs` 실행 시 vault에 노트가 생성됨
  - frontmatter가 올바르게 삽입됨
  - 기존 노트 덮어쓰기가 정상 동작
- **Complexity**: Medium

### Step 4: save-idea skill

- **Goal**: 아이디어 메모를 vault에 저장하는 skill 구현
- **Specs Reference**: TS-4
- **Files**:
  - `plugins/local-memory/skills/save-idea/SKILL.md` - Create - skill 정의
- **Details**:
  - 인자에서 제목 파싱, 태그 옵션 처리 (`--tag`)
  - 제목 slug화 → 파일명 생성
  - Obsidian frontmatter 생성 (source, repo, type, created, tags)
  - `obsidian create ... silent` 명령으로 vault의 `{repo-name}/ideas/`에 저장
  - 동일 이름 존재 시 사용자에게 덮어쓰기 확인
  - 아이디어 목록 조회 기능 (`obsidian search query="path:{repo-name}/ideas"`)
- **Validation**:
  - `/save-idea "테스트 아이디어"` 실행 시 vault에 노트가 생성됨
  - 태그 옵션이 frontmatter에 반영됨
- **Complexity**: Medium

### Step 5: 마켓플레이스 등록

- **Goal**: 마켓플레이스 README 및 plugin.json에 local-memory 플러그인 등록
- **Specs Reference**: TS-1
- **Files**:
  - `README.md` - Modify - 플러그인 목록에 local-memory 추가
  - `.claude-plugin/plugin.json` - Modify - 마켓플레이스 매니페스트 업데이트 (필요 시)
- **Details**:
  - README.md의 플러그인 테이블에 local-memory 행 추가
  - 설치 명령어 및 의존성 안내 포함
- **Validation**:
  - README.md에 local-memory 플러그인 정보가 표시됨
- **Complexity**: Simple

## Task Breakdown

- [ ] **Step 1**: 플러그인 디렉토리 구조 및 plugin.json 생성
- [ ] **Step 2**: repo-memory 에이전트 playbook 작성 (Pre-flight check 포함)
- [ ] **Step 3**: sync-specs skill 작성
- [ ] **Step 4**: save-idea skill 작성
- [ ] **Step 5**: 마켓플레이스 README 업데이트
- [ ] **Final**: 전체 acceptance criteria 검증

## File Change Summary

| File | Action | Step | Description |
|------|--------|------|-------------|
| `plugins/local-memory/plugin.json` | Create | 1 | 플러그인 매니페스트 (의존성 포함) |
| `plugins/local-memory/README.md` | Create | 1 | 플러그인 설명 문서 |
| `plugins/local-memory/commands/` | Create | 1 | commands 디렉토리 |
| `plugins/local-memory/agents/repo-memory/AGENT.md` | Create | 2 | repo-memory 에이전트 playbook |
| `plugins/local-memory/skills/sync-specs/SKILL.md` | Create | 3 | specs 동기화 skill |
| `plugins/local-memory/skills/save-idea/SKILL.md` | Create | 4 | 아이디어 메모 skill |
| `README.md` | Modify | 5 | 마켓플레이스 플러그인 목록 업데이트 |

## Dependencies Between Steps

```
Step 1 ─── Step 2 ─── Step 3
               │
               └────── Step 4
                          │
Step 5 (Step 1 이후 언제든 가능)
```

- Step 2, 3, 4는 모두 Step 1(스캐폴딩)에 의존
- Step 3, 4는 Step 2(에이전트)의 Pre-flight check 및 repo name 추출 로직을 참조
- Step 3과 Step 4는 서로 독립적으로 병렬 가능
- Step 5는 Step 1 이후 언제든 가능

## Testing Strategy

### Manual Verification

1. **Pre-flight check**: Obsidian 앱 미실행 상태에서 skill 실행 → 안내 메시지 출력 확인
2. **sync-specs**: 현재 repo의 `specs/create-local-memory-plugin/`을 vault에 동기화 → vault에서 노트 확인
3. **save-idea**: `/save-idea "테스트 아이디어 --tag test"` 실행 → vault의 `{repo-name}/ideas/`에 노트 생성 확인
4. **frontmatter**: 동기화된 노트의 frontmatter가 올바른 형식인지 확인

## Rollback Plan

1. **After Step 1-4**: `plugins/local-memory/` 디렉토리 삭제
2. **After Step 5**: README.md의 해당 행 삭제, git revert 가능

모든 변경이 새 파일 생성이므로 rollback 위험이 낮음. Step 5의 README 수정만 기존 파일 변경.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Obsidian CLI 버전 호환성 | Medium | Medium | Pre-flight check에서 버전 확인, 인스톨러 업데이트 안내 |
| vault 이름에 특수문자 포함 | Low | Low | repo name slug화 적용 |
| obsidian-skills plugin.json dependencies 필드 미지원 | Medium | Low | README에 수동 설치 안내 병기 |

## Progress Tracking

| Step | Status | Started | Completed | Notes |
|------|--------|---------|-----------|-------|
| Step 1 | Pending | | | |
| Step 2 | Pending | | | |
| Step 3 | Pending | | | |
| Step 4 | Pending | | | |
| Step 5 | Pending | | | |

## Acceptance Criteria Checklist

From requirements:

**FR-1: obsidian-skills 의존성**
- [ ] plugin.json에 `kepano/obsidian-skills`를 의존성으로 명시
- [ ] obsidian-skills 미설치 시 사용자에게 설치 안내 제공
- [ ] Obsidian 앱 설치 여부 및 CLI 지원 버전 사전 검사
- [ ] Obsidian 앱 미실행 시 실행 안내

**FR-2: repo-memory 에이전트**
- [ ] `agents/repo-memory/` 경로에 에이전트 playbook 존재
- [ ] 현재 git repo name 자동 감지
- [ ] repo name 기준 vault 내 폴더 구조화

**FR-3: specs 동기화 skill**
- [ ] `skills/sync-specs/` 경로에 skill 존재
- [ ] specs 디렉토리의 문서를 Obsidian vault에 저장
- [ ] vault 내 저장 경로 `{repo-name}/specs/{task-name}/` 구조
- [ ] 문서 변경 시 vault 노트 업데이트
- [ ] 메타데이터가 Obsidian frontmatter로 보존

**FR-4: 아이디어 메모 skill**
- [ ] `skills/save-idea/` 경로에 skill 존재
- [ ] `{repo-name}/ideas/` 하위에 저장
- [ ] 제목, 내용, 태그, 생성일 포함
- [ ] 저장된 아이디어 목록 조회 가능
