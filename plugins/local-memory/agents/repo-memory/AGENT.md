---
name: repo-memory
description: GitHub repo 단위 외부기억을 Obsidian vault 또는 로컬 파일시스템에 관리하는 에이전트. sync-specs, save-idea skill 실행 시 사전 검사 및 repo 컨텍스트를 제공한다.
---

# repo-memory Agent

GitHub repo 단위로 외부기억을 저장·관리한다. 백엔드 설정에 따라 Obsidian vault, 로컬 파일시스템, 또는 git 저장소를 사용한다.

> 백엔드별 명령어는 `references/backend-operations.md`를 참조한다.

## Pre-flight Check

skill을 실행하기 전에 반드시 아래 검사를 순서대로 수행한다. 실패 시 해당 단계의 안내 메시지를 출력하고 중단한다.

### 1. Git 저장소 확인

```bash
git rev-parse --show-toplevel
```

- 실패 시: "현재 디렉토리가 git 저장소가 아닙니다. git 저장소에서 실행해주세요."

### 2. 백엔드 설정 확인

`.claude/local-memory.json`에서 `backend` 값을 읽는다 (기본값: `"obsidian"`).

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

## Vault 설정 읽기

1. `.claude/local-memory.json` 파일을 읽는다
2. `backend` 키에서 백엔드를 확인한다 (기본값: `"obsidian"`)
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
  "vault": "MyVault",
  "directory": "claude-memory",
  "basePath": "/home/user/claude-memory-store",
  "gitAutoCommit": true,
  "gitRemote": "origin"
}
```

- `backend` (선택): `"obsidian"` (기본값) | `"filesystem"` | `"git"`
- `vault` (obsidian 필수): Obsidian vault 이름
- `basePath` (filesystem/git 필수): 저장소 루트 절대 경로
- `directory` (선택): 하위 디렉토리 이름 (기본값: `claude-memory`)
- `gitAutoCommit` (선택): git 백엔드 자동 커밋 여부 (기본값: `true`)
- `gitRemote` (선택): git 백엔드 push 대상 remote (기본값: `"origin"`)

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

repo name이 확인되면 저장소 내 폴더 구조를 준비한다:

### backend = obsidian

```bash
obsidian vault="{vault-name}" create name="{repo-name}" path="{directory}" content="---\ntype: repo-index\nrepo: {repo-name}\ntags:\n  - repo/{repo-name}\n---\n\n# {repo-name}\n\nGitHub repo 외부기억 인덱스.\n\n## Specs\n\n![[{directory}/{repo-name}/specs]]\n\n## Ideas\n\n![[{directory}/{repo-name}/ideas]]" silent
```

### backend = filesystem / git

```bash
mkdir -p "{basePath}/{directory}/{repo-name}"
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

## Ideas

- [ideas](./{repo-name}/ideas/)
EOF
```

> filesystem/git 백엔드에서는 Obsidian wikilinks (`![[...]]`) 대신 표준 마크다운 링크를 사용한다.

## Skill 조율

이 에이전트는 아래 skill들의 실행 컨텍스트를 제공한다:

- **sync-specs**: specs 문서를 저장소에 동기화
- **save-idea**: 아이디어 메모를 저장소에 저장

각 skill 실행 전에:
1. Pre-flight check를 수행한다
2. 백엔드, vault/basePath, repo name을 확인한다
3. 해당 정보를 skill에 전달한다
