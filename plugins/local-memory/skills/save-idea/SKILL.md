---
name: save-idea
description: 아이디어 메모를 Obsidian vault에 저장한다. 현재 repo의 {directory}/{directory}/{repo-name}/ideas/ 경로에 노트를 생성한다. Use when the user wants to save an idea, memo, or note to Obsidian, or mentions "아이디어 저장", "메모 저장", "save idea", "save memo".
---

# save-idea

GitHub repo 작업 중 발생하는 아이디어, 메모를 Obsidian vault에 저장하는 skill.

## Input

사용자가 `/save-idea` 실행 시 인자로 제목과 옵션을 전달한다.

- `/save-idea "API 리팩토링 아이디어"` — 제목만 전달 (내용은 대화에서 수집)
- `/save-idea "API 리팩토링 아이디어" --tag api,refactoring` — 제목 + 태그

인자가 없으면 AskUserQuestion으로 제목을 물어본다.

## Process

### Step 1: 컨텍스트 확인

repo-memory 에이전트의 Pre-flight check를 수행하여 vault-name, directory, repo-name을 확인한다.

- `vault-name`: `.claude/settings.local.json`의 `local-memory.vault`
- `directory`: `.claude/settings.local.json`의 `local-memory.directory` (기본값: `claude-memory`)
- `repo-name`: git remote 또는 디렉토리명에서 추출

### Step 2: 입력 파싱

1. 인자에서 제목을 추출한다 (따옴표로 감싸진 텍스트)
2. `--tag` 옵션이 있으면 태그 목록을 파싱한다 (쉼표 구분)
3. 제목이 없으면 AskUserQuestion으로 물어본다

### Step 3: 내용 수집

인자에 내용이 포함되지 않았으면 사용자에게 아이디어 내용을 물어본다:

- "아이디어 내용을 입력해주세요. (자유 형식)"

### Step 4: Slug 생성

제목을 파일명으로 사용할 slug로 변환한다:

- 한글은 유지한다 (Obsidian은 한글 파일명 지원)
- 공백을 하이픈으로 대체
- 특수문자 제거 (알파벳, 숫자, 한글, 하이픈만 허용)
- 연속 하이픈 정리

### Step 5: 중복 확인

```bash
obsidian vault="{vault-name}" search query="path:{directory}/{repo-name}/ideas/{slug}" limit=1
```

동일 이름이 존재하면 AskUserQuestion으로 덮어쓰기 여부를 확인한다:
- "이미 동일한 이름의 아이디어가 존재합니다. 덮어쓰시겠습니까?"
  - 덮어쓰기 → `overwrite` 플래그 추가
  - 취소 → 중단

### Step 6: Vault에 저장

#### Frontmatter 형식

```yaml
---
source: repo
repo: {repo-name}
type: idea
created: {YYYY-MM-DD}
tags:
  - repo/{repo-name}
  - idea
  - {사용자 태그 각각}
---
```

#### Obsidian CLI 명령

```bash
obsidian vault="{vault-name}" create name="{slug}" path="{directory}/{repo-name}/ideas" content="{frontmatter}\n\n# {원본 제목}\n\n{아이디어 내용}" silent
```

덮어쓰기인 경우 `overwrite` 플래그 추가.

### Step 7: 결과 보고

```
아이디어 저장 완료: {vault-name}

  파일: {directory}/{repo-name}/ideas/{slug}.md
  제목: {원본 제목}
  태그: {태그 목록}
```

## 아이디어 목록 조회

사용자가 "아이디어 목록", "ideas list" 등을 요청하면:

```bash
obsidian vault="{vault-name}" search query="path:{directory}/{repo-name}/ideas" limit=20
```

결과를 테이블 형태로 정리하여 출력한다:

```
{repo-name} 아이디어 목록:

| # | 제목 | 생성일 | 태그 |
|---|------|--------|------|
| 1 | ... | ... | ... |
```
