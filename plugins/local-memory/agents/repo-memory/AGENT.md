---
name: repo-memory
description: GitHub repo 단위 외부기억을 선택된 백엔드(obsidian / filesystem / git)에 관리하는 에이전트. sync-specs, sync-scripts, save-idea skill 실행 시 사전 검사·repo 컨텍스트·scope 라우팅을 제공한다.
---

# repo-memory Agent

GitHub repo 단위로 외부기억을 저장·관리한다. 설정된 백엔드에 따라 obsidian vault, 로컬 파일시스템, 또는 git 저장소를 사용한다.

> 백엔드별 명령어는 `references/backend-operations.md`를, 스크립트 카테고리와 자연어 의도 사전은 `references/script-sources.md`를 참조한다.

## Skill 호출 계약 (scope 인자)

본 에이전트를 호출하는 모든 skill은 `scope` 인자를 명시한다.

| scope | 의미 | 호출 skill |
|-------|------|----------|
| `specs` | spec 문서(requirements / specs / plans) 영역 | `sync-specs` |
| `scripts` | 저장소 스크립트(bash / makefile / django-command) 영역 | `sync-scripts` |
| `all` | 두 영역 통합 검색·점검 | `/check-settings` 등 영역 무관 사용처 |

- 호출 인자가 비어 있으면 에이전트는 `AskUserQuestion`으로 "specs / scripts / all 중 어느 범위를 동기화·검색할까요?"를 묻고 명시적 응답 후에만 진행한다 (기본값 무음 적용 금지)
- 출력 진행/오류 메시지는 영역 라벨을 접두로 사용한다: `[specs]` 또는 `[scripts]`. `scope=all`인 경우 영역별로 분리된 메시지를 각각 출력한다 (한 메시지에서 두 영역 혼합 금지)

## Pre-flight Check

skill을 실행하기 전에 반드시 아래 검사를 순서대로 수행한다. 실패 시 해당 단계의 안내 메시지를 출력하고 중단한다.

### 1. Git 저장소 확인

```bash
git rev-parse --show-toplevel
```

- 실패 시: "현재 디렉토리가 git 저장소가 아닙니다. git 저장소에서 실행해주세요."

### 2. 백엔드 설정 확인

`.claude/local-memory.json`에서 `backend` 값을 읽는다.

> Note: 값이 미설정인 경우 동작 호환을 위해 `obsidian`이 적용되지만, 신규 사용자 흐름(`/check-settings`)에서는 항상 명시 선택을 권장한다.

### 3. 백엔드별 환경 검사

#### backend = obsidian

```bash
# 3a. Obsidian 앱 설치 확인
test -d "/Applications/Obsidian.app"
```

- 실패 시: "Obsidian 앱이 설치되어 있지 않습니다. https://obsidian.md/download 에서 다운로드하세요."

```bash
# 3b. Obsidian 앱 실행 및 CLI 확인
obsidian help
```

- 정상 응답이 없거나 "out of date" 경고만 나오면:
  - "Obsidian 앱을 실행한 후 다시 시도하세요."
  - 인스톨러 구버전 경고 시: "최신 인스톨러로 업데이트하세요: https://obsidian.md/download"

```bash
# 3c. Vault 통신 확인
obsidian vault="{vault-name}" search query="test" limit=1
```

- 실패 시: "vault '{vault-name}'에 접근할 수 없습니다. Obsidian 앱에서 해당 vault가 열려 있는지 확인하세요."

#### backend = filesystem

```bash
# 3a. basePath 존재 확인
test -d "{basePath}"
```

- 실패 시: "basePath '{basePath}'가 존재하지 않습니다. 디렉토리를 생성하거나 경로를 확인하세요."

```bash
# 3b. 쓰기 권한 확인
test -w "{basePath}"
```

- 실패 시: "basePath '{basePath}'에 쓰기 권한이 없습니다."

#### backend = git

```bash
# 3a. basePath 존재 확인
test -d "{basePath}"
```

- 실패 시: "basePath '{basePath}'가 존재하지 않습니다."

```bash
# 3b. 쓰기 권한 확인
test -w "{basePath}"
```

- 실패 시: "basePath '{basePath}'에 쓰기 권한이 없습니다."

```bash
# 3c. git 저장소 확인
git -C "{basePath}" rev-parse --is-inside-work-tree
```

- 실패 시: "basePath '{basePath}'가 git 저장소가 아닙니다. `git init`으로 초기화하세요."

> Pre-flight 출력에서 영역별 보고가 필요한 경우 `[specs]` / `[scripts]` 라벨을 접두로 분리하여 출력한다.

## 백엔드 설정 읽기

1. `.claude/local-memory.json` 파일을 읽는다
2. `backend` 키에서 백엔드를 확인한다
3. 백엔드별 필수 설정을 확인한다:
   - **obsidian**: `vault` (필수)
   - **filesystem / git**: `basePath` (필수)
4. `directory` 키에서 하위 디렉토리 이름을 가져온다 (기본값: `claude-memory`)
5. 파일이 없거나 필수 설정이 누락되면 사용자에게 물어본다 (AskUserQuestion 사용)
6. 사용자가 입력한 값을 `.claude/local-memory.json`에 저장한다

**설정 파일**: `.claude/local-memory.json` (전용 설정 파일, settings.local.json과 분리)

```json
{
  "backend": "filesystem",
  "directory": "claude-memory",
  "basePath": "/Users/jongtaek.hwang/Projects/datamaker-docs",
  "gitAutoCommit": true,
  "gitRemote": "origin"
}
```

- `backend` (선택): `"obsidian"` | `"filesystem"` | `"git"` ([Note](#backend-default))
- `vault` (obsidian 필수): obsidian vault 이름
- `basePath` (filesystem / git 필수): 저장소 루트 절대 경로
- `directory` (선택): 하위 디렉토리 이름 (기본값: `claude-memory`)
- `gitAutoCommit` (선택): git 백엔드 자동 커밋 여부 (기본값: `true`)
- `gitRemote` (선택): git 백엔드 push 대상 remote (기본값: `"origin"`)

<a id="backend-default"></a>
> Note: `backend` 미설정 시 동작 호환을 위해 `obsidian`이 적용된다. 신규 사용자 흐름은 `/check-settings`로 명시 선택을 권장한다.

## Repo Name 추출

현재 작업 디렉토리의 git repo name을 추출한다:

```bash
# 1차: GitHub remote에서 추출
git remote get-url origin 2>/dev/null | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\///'

# fallback: git root 디렉토리명
basename $(git rev-parse --show-toplevel)
```

추출된 repo name은 `{directory}/{repo-name}/` 경로에서 사용한다.

## 저장소 폴더 구조 초기화

repo name이 확인되면 저장소 내 폴더 구조를 준비한다. `scope` 인자가 `scripts` 또는 `all`이면 `scripts/<카테고리>/` 디렉토리도 함께 생성한다.

### backend = obsidian

```bash
obsidian vault="{vault-name}" create name="{repo-name}" path="{directory}" content="---\ntype: repo-index\nrepo: {repo-name}\ntags:\n  - repo/{repo-name}\n---\n\n# {repo-name}\n\nGitHub repo 외부기억 인덱스.\n\n## Specs\n\n![[{directory}/{repo-name}/specs]]\n\n## Scripts\n\n![[{directory}/{repo-name}/scripts]]\n\n## Ideas\n\n![[{directory}/{repo-name}/ideas]]" silent
```

`scope`가 `scripts` 또는 `all`이면 카테고리 placeholder 노트를 만들거나 디렉토리가 obsidian search로 인지되도록 첫 노트 생성을 보장한다 (필요 시 빈 `.gitkeep` 등가 노트).

### backend = filesystem / git

```bash
mkdir -p "{basePath}/{directory}/{repo-name}"
# scope=scripts 또는 all 일 때 추가:
mkdir -p "{basePath}/{directory}/{repo-name}/scripts/bash"
mkdir -p "{basePath}/{directory}/{repo-name}/scripts/makefile"
mkdir -p "{basePath}/{directory}/{repo-name}/scripts/django-command"

cat > "{basePath}/{directory}/{repo-name}/{repo-name}.md" << 'EOF'
---
type: repo-index
repo: {repo-name}
tags:
  - repo/{repo-name}
---

# {repo-name}

GitHub repo 외부기억 인덱스.

## Specs

- [specs](./{repo-name}/specs/)

## Scripts

- [scripts](./{repo-name}/scripts/)

## Ideas

- [ideas](./{repo-name}/ideas/)
EOF
```

> filesystem/git 백엔드에서는 obsidian wikilinks (`![[...]]`) 대신 표준 마크다운 링크를 사용한다.

## 인덱스 노트 비파괴 병합 (Plugin Update Migration)

업그레이드(v2.0.0 → v2.1.0) 또는 처음 `scope=scripts|all` 호출 시 기존 인덱스 노트를 손상시키지 않고 `## Scripts` 섹션만 안전하게 추가한다.

### 알고리즘

1. **존재 확인**: 백엔드별 EXISTS로 `{directory}/{repo-name}/{repo-name}.md` 확인
2. **미존재** → "저장소 폴더 구조 초기화"의 신규 템플릿(specs / scripts / ideas 3섹션)으로 생성하고 종료
3. **존재** → READ로 본문 로드
4. 본문 라인 단위 정확 일치 검사: 정규식 `^## Scripts\s*$`
5. **이미 존재** → no-op (idempotency 보장)
6. **부재** → 다음 블록을 삽입할 위치 결정:
   - 본문에 `^## Ideas\s*$` 라인이 있으면 그 직전 빈 줄 위치에 삽입
   - 없으면 본문 끝에 append
7. 삽입할 블록:
   - obsidian:
     ```markdown
     ## Scripts

     ![[{directory}/{repo-name}/scripts]]
     ```
   - filesystem / git:
     ```markdown
     ## Scripts

     - [scripts](./{repo-name}/scripts/)
     ```
8. 백엔드별 CREATE(overwrite)로 노트 전체를 다시 쓴다. 사용자가 직접 작성한 다른 섹션·문구는 보존

### 호출 시점

- `repo-memory(scope=scripts)` 또는 `repo-memory(scope=all)`이 호출될 때마다 본 절차를 수행 (idempotent)
- `repo-memory(scope=specs)` 호출에서는 본 절차를 건너뛴다 — 기존 동작 무회귀

## Skill 조율

이 에이전트는 아래 skill들의 실행 컨텍스트를 제공한다:

- **sync-specs** (`scope=specs`): spec 문서를 저장소에 동기화
- **sync-scripts** (`scope=scripts`): 저장소 스크립트를 외부기억에 동기화
- **save-idea**: 아이디어 메모를 저장소에 저장

각 skill 실행 전에:

1. Pre-flight check를 수행한다
2. 백엔드, vault/basePath, repo name을 확인한다
3. `scope` 인자에 따라 폴더 초기화·인덱스 노트 병합을 수행한다 (해당 영역 한정)
4. 해당 정보를 skill에 전달한다
5. 출력은 `[specs]` / `[scripts]` 라벨을 접두로 분리하여 보고한다
