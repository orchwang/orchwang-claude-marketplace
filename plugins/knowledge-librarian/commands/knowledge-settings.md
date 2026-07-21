---
name: knowledge-settings
description: knowledge-librarian 플러그인의 지식 소스 설정을 검토하고, 누락 항목을 대화형으로 설정한다.
---

# knowledge-settings

`knowledge-librarian`이 현재 repo 환경에서 정상 동작하기 위한 설정(`.claude/knowledge-librarian.json`)을 검토하고, 누락 항목을 안내·설정하는 command.

> 설정 스키마는 `references/source-config.md`를 참조한다. 본 설정 파일은 `local-memory.json`과 **완전히 분리**된다.

## Input

`/knowledge-settings` — 인자 없이 실행

## Process

### Step 1: 설정 파일 검사

`.claude/knowledge-librarian.json`을 읽는다. 각 항목을 OK / MISSING / WARNING으로 분류한다.

- 파일 없음 → MISSING: 신규 설정 흐름(Step 3)으로 진행
- `sources[]` 비어 있음 → MISSING: 소스 추가 안내
- `backend` 미설정 → WARNING: 기본 `git` 적용 안내

### Step 2: 소스 접근성 검사 (read-only)

각 소스에 대해:

#### backend = filesystem / git

```bash
test -d "{basePath}"                 # 소스 루트 존재
test -d "{basePath}/{root}"          # 각 root 존재
```

- basePath 없음 → MISSING
- 개별 root 없음 → WARNING (해당 root만 스킵됨)
- 쓰기 권한은 검사하지 않는다 (read-only)

#### backend = obsidian

```bash
obsidian vault="{vault}" search query="test" limit=1
```

- 실패 → MISSING: "vault '{vault}'에 접근할 수 없습니다."

### Step 3: 누락 항목 대화형 설정

`AskUserQuestion`으로 아래를 순서대로 물어 설정을 구성한다:

1. `backend` (obsidian / filesystem / git — 기본 git)
2. 소스 `name`
3. 위치: filesystem/git이면 `basePath`, obsidian이면 `vault`
4. `roots[]` (예: `_posts/`) — 소스 내 지식 위치
5. `exclude[]` (선택, 예: `**/_site/**`)

입력값을 `.claude/knowledge-librarian.json`에 저장한다.

### Step 4: 인덱스 위치 안내

- `indexPath`(기본 `.claude/knowledge-index.json`)는 현재 repo에 저장되며 소스는 변경되지 않음을 안내한다
- `AskUserQuestion`으로 `indexPath`를 현재 repo `.gitignore`에 추가할지 확인한다 (기본 권장: 추가 — 인덱스는 로컬 캐시 성격)

### Step 5: 결과 보고

```
[librarian] 설정 검토 결과

  backend: git (OK)
  indexPath: .claude/knowledge-index.json (OK)
  소스:
    - blog: /Users/.../orchwang.github.io [_posts/] (OK)

다음 단계: /knowledge-index 로 카탈로그를 구축하세요.
```

## Note: local-memory와의 관계

- 설정 파일과 명령이 `local-memory`와 분리되어 있어 두 플러그인을 동시에 사용할 수 있다.
- `local-memory`는 작업 산출물을 **write-out**, `knowledge-librarian`은 wiki 지식을 **read-in** 한다.
- 필요 시 `local-memory`가 저장한 `{repo}/specs/` 트리를 본 플러그인의 지식 소스로 지정할 수도 있다 (선택).
