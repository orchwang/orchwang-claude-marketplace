# Specs: Create local-memory plugin

> Created: 2026-03-07
> Updated: 2026-03-07
> Status: Ready
> Requirements: [requirements.md](./requirements.md)

## Overview

`local-memory` 플러그인은 Claude Code가 GitHub repo 작업 중 생성하는 컨텍스트를 Obsidian vault에 외부기억으로 저장·관리한다. Obsidian vault CRUD는 `kepano/obsidian-skills` 플러그인에 위임하고, 본 플러그인은 repo 단위 컨텍스트 분류·관리 계층만 담당한다.

## Technical Specifications

### TS-1: 플러그인 매니페스트 및 의존성

- 플러그인 코드: `local-memory`
- 플러그인 경로: `plugins/local-memory/`
- `plugin.json`에 `kepano/obsidian-skills` 의존성 명시
- 기존 `plugins/orchwang-general/` 패턴을 따름

```json
{
  "name": "local-memory",
  "version": "1.0.0",
  "description": "GitHub repo 단위 외부기억을 Obsidian vault에 저장·관리하는 플러그인",
  "author": { "name": "orchwang" },
  "repository": "https://github.com/orchwang/orchwang-claude-marketplace.git",
  "license": "MIT",
  "keywords": ["obsidian", "memory", "vault", "repo-context"],
  "dependencies": ["kepano/obsidian-skills"],
  "commands": [],
  "skills": ["sync-specs", "save-idea"],
  "agents": ["repo-memory"]
}
```

### TS-2: repo-memory 에이전트

- 경로: `plugins/local-memory/agents/repo-memory/`
- 에이전트 playbook 파일: `AGENT.md`
- 역할: obsidian-skills의 `obsidian` CLI를 활용하여 repo 단위 외부기억을 관리

**핵심 동작:**

1. `git remote get-url origin` 또는 현재 디렉토리의 `.git` 정보에서 repo name 추출
2. `.claude/settings.local.json`에서 vault 이름 읽기 (미설정 시 사용자에게 질문 후 저장)
3. vault 내 `{repo-name}/` 폴더 존재 여부 확인, 없으면 생성 지시
4. 하위 skill(sync-specs, save-idea)을 조율하여 컨텍스트 저장

**Vault 폴더 구조:**

```
vault/
  {repo-name}/
    specs/
      {task-name}/
        requirements.md
        specs.md
        plans.md
    ideas/
      {idea-slug}.md
```

**Repo name 추출 로직:**

```bash
# GitHub remote에서 추출
git remote get-url origin | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\///'
# fallback: 디렉토리명
basename $(git rev-parse --show-toplevel)
```

### TS-3: sync-specs skill

- 경로: `plugins/local-memory/skills/sync-specs/`
- skill 정의: `SKILL.md`
- 트리거: 사용자가 `/sync-specs` 실행 또는 repo-memory 에이전트가 호출

**동작 흐름:**

1. 현재 repo의 `specs/` 디렉토리에서 모든 task 디렉토리 스캔
2. 각 task의 requirements.md, specs.md, plans.md를 읽음
3. `obsidian create` 또는 기존 노트가 있으면 덮어쓰기로 vault에 저장
4. Obsidian frontmatter에 메타데이터 삽입

**Obsidian 노트 형식 (예: requirements.md):**

```markdown
---
source: repo
repo: orchwang-claude-marketplace
task: create-local-memory-plugin
type: requirements
status: Draft
synced: 2026-03-07
tags:
  - repo/orchwang-claude-marketplace
  - specs
  - requirements
---

{requirements.md 원본 내용}
```

**사용하는 obsidian CLI 명령:**

```bash
# 노트 생성/덮어쓰기
obsidian create name="{task-name}-requirements" path="{repo-name}/specs/{task-name}" content="..." overwrite silent

# 속성 설정
obsidian property:set name="synced" value="{날짜}" path="{repo-name}/specs/{task-name}/{task-name}-requirements.md"
```

### TS-4: save-idea skill

- 경로: `plugins/local-memory/skills/save-idea/`
- skill 정의: `SKILL.md`
- 트리거: 사용자가 `/save-idea` 실행

**입력:** 제목, 내용, 태그(선택)

**동작 흐름:**

1. 사용자에게 아이디어 제목과 내용 수집 (AskUserQuestion 또는 인자로 전달)
2. 제목을 slug화하여 파일명 생성
3. `obsidian create`로 vault의 `{repo-name}/ideas/` 하위에 노트 생성

**Obsidian 노트 형식:**

```markdown
---
source: repo
repo: orchwang-claude-marketplace
type: idea
created: 2026-03-07
tags:
  - repo/orchwang-claude-marketplace
  - idea
  - {사용자 태그}
---

# {아이디어 제목}

{아이디어 내용}
```

**사용하는 obsidian CLI 명령:**

```bash
# 아이디어 노트 생성
obsidian create name="{idea-slug}" path="{repo-name}/ideas" content="..." silent

# 아이디어 목록 조회
obsidian search query="path:{repo-name}/ideas" limit=20
```

### TS-5: 사전 검사 (Pre-flight Check)

repo-memory 에이전트가 동작하기 전에 수행하는 검증:

1. **Obsidian 앱 설치 확인**: `/Applications/Obsidian.app` 존재 여부
2. **Obsidian 앱 실행 확인**: `obsidian help` 명령이 정상 응답하는지 확인
3. **obsidian-skills 설치 확인**: `obsidian:obsidian-cli` skill이 사용 가능한지 확인
4. **Vault 접근 확인**: `obsidian search query="test" limit=1`로 vault 통신 가능 여부 확인

실패 시 각 단계별 안내 메시지 제공.

## Architecture

```
┌─────────────────────────────────────┐
│         local-memory plugin         │
│                                     │
│  ┌─────────────┐  ┌──────────────┐  │
│  │ repo-memory  │  │  Pre-flight  │  │
│  │   agent      │──│   Check      │  │
│  └──────┬───────┘  └──────────────┘  │
│         │                            │
│  ┌──────┴───────┐  ┌──────────────┐  │
│  │  sync-specs  │  │  save-idea   │  │
│  │    skill     │  │    skill     │  │
│  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼──────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────┐
│    kepano/obsidian-skills plugin    │
│  (obsidian-cli, obsidian-markdown)  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   Obsidian App (내장 CLI)            │
│   └─ Vault: {repo-name}/           │
│       ├─ specs/{task}/              │
│       └─ ideas/                     │
└─────────────────────────────────────┘
```

## API / Interface Design

### Slash Commands (user-invocable skills)

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/sync-specs` | specs 문서를 Obsidian vault에 동기화 | `[task-name]` (생략 시 전체) |
| `/save-idea` | 아이디어 메모를 vault에 저장 | `"제목" [--tag tag1,tag2]` |

### Agent Triggers

| Agent | Trigger |
|-------|---------|
| `repo-memory` | `/sync-specs`, `/save-idea` 실행 시 사전 검사 및 repo context 제공 |

## Error Handling

| 상황 | 처리 |
|------|------|
| Obsidian 앱 미설치 | 설치 안내 + 다운로드 링크 (`https://obsidian.md/download`) 제공 |
| Obsidian 앱 미실행 | "Obsidian 앱을 실행한 후 다시 시도하세요" 안내 |
| obsidian-skills 미설치 | 설치 명령어 안내 |
| vault 통신 실패 | CLI 오류 메시지 표시 + 앱 상태 확인 안내 |
| git repo가 아닌 디렉토리 | "git 저장소에서만 사용 가능합니다" 안내 |
| specs 디렉토리 없음 | "specs/ 디렉토리가 없습니다" 안내 |
| 동일 이름 아이디어 존재 | 사용자에게 덮어쓰기 여부 확인 |

## Dependencies

### 외부 의존성

- **kepano/obsidian-skills** (Claude Code plugin) — vault 상호작용 전체 위임
- **Obsidian App v1.12+** — 내장 CLI 제공

### 내부 의존성

- **orchwang-marketplace** — 플러그인 등록 및 배포

### TS-6: Vault 설정

대상 vault는 `.claude/settings.json` 또는 `.claude/settings.local.json`에서 지정한다.

```json
{
  "local-memory": {
    "vault": "MyVault"
  }
}
```

- 에이전트/skill은 설정에서 vault 이름을 읽어 `vault="{name}"` 파라미터로 전달
- 설정이 없으면 사용자에게 vault 이름을 물어보고 `settings.local.json`에 저장
- Obsidian CLI는 `vault=` 미지정 시 가장 최근 포커스된 vault를 사용 (fallback)

## Open Questions

- sync-specs 실행을 SDD 워크플로우 종료 시 자동 트리거할 것인가, 수동 실행만 지원할 것인가?
