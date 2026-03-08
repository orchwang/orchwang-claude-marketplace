---
name: sync-specs
description: specs 문서(requirements, specs, plans)를 Obsidian vault에 동기화한다. 현재 repo의 specs/ 디렉토리를 스캔하여 vault의 {directory}/{repo-name}/specs/{task-name}/ 경로에 저장한다. Use when the user wants to sync spec documents to Obsidian, or mentions "sync specs", "obsidian에 저장", "vault에 동기화".
---

# sync-specs

specs 문서를 Obsidian vault에 동기화하는 skill.

## Input

사용자가 `/sync-specs` 실행 시 선택적으로 task-name을 인자로 전달할 수 있다.

- `/sync-specs` — 전체 task 동기화
- `/sync-specs create-local-memory-plugin` — 특정 task만 동기화

## Process

### Step 1: 컨텍스트 확인

repo-memory 에이전트의 Pre-flight check를 수행하여 vault-name, directory, repo-name을 확인한다.

- `vault-name`: `.claude/local-memory.json`의 `vault`
- `directory`: `.claude/local-memory.json`의 `directory` (기본값: `claude-memory`)
- `repo-name`: git remote 또는 디렉토리명에서 추출

### Step 2: Task 목록 수집

```bash
# specs/ 하위의 모든 task 디렉토리 목록
ls -d specs/*/
```

인자로 task-name이 지정된 경우 해당 task만 대상으로 한다.

- task-name에 해당하는 디렉토리가 없으면: "specs/{task-name}/ 디렉토리를 찾을 수 없습니다." 안내 후 중단

### Step 3: 각 Task의 문서 동기화

각 task 디렉토리에 대해 requirements.md, specs.md, plans.md를 순회한다.

각 파일에 대해:

1. **파일 읽기**: Read 도구로 파일 내용을 읽는다
2. **frontmatter 생성**: 아래 형식으로 Obsidian frontmatter를 준비한다
3. **vault에 저장**: `obsidian create` 명령으로 저장한다

#### Frontmatter 형식

```yaml
---
source: repo
repo: {repo-name}
task: {task-name}
type: {requirements | specs | plans}
synced: {YYYY-MM-DD}
tags:
  - repo/{repo-name}
  - specs
  - {type}
---
```

#### Obsidian CLI 명령

```bash
obsidian vault="{vault-name}" create name="{task-name}-{type}" path="{directory}/{repo-name}/specs/{task-name}" content="{frontmatter + 원본 내용}" overwrite silent
```

- `name`: `{task-name}-requirements`, `{task-name}-specs`, `{task-name}-plans`
- `path`: `{repo-name}/specs/{task-name}`
- `overwrite`: 기존 노트가 있으면 덮어쓰기
- `silent`: Obsidian 앱에서 노트를 열지 않음

### Step 4: 결과 보고

동기화 완료 후 결과를 출력한다:

```
Obsidian vault 동기화 완료: {vault-name}

동기화된 문서:
  - {directory}/{repo-name}/specs/{task-name}/requirements.md
  - {directory}/{repo-name}/specs/{task-name}/specs.md
  - {directory}/{repo-name}/specs/{task-name}/plans.md

총 {N}개 task, {M}개 문서 동기화됨
```

## Content 전달 시 주의사항

- `obsidian create`의 `content` 값에 줄바꿈은 `\n`, 탭은 `\t`로 이스케이프한다
- 큰따옴표가 포함된 내용은 이스케이프 처리한다
- frontmatter의 `---` 구분자가 content에 포함되어야 한다
- 원본 문서에 이미 frontmatter가 있으면 제거 후 새 frontmatter로 교체한다
