---
name: repo-memory
description: GitHub repo 단위 외부기억을 Obsidian vault에 관리하는 에이전트. sync-specs, save-idea skill 실행 시 사전 검사 및 repo 컨텍스트를 제공한다.
---

# repo-memory Agent

GitHub repo 단위로 Obsidian vault에 외부기억을 저장·관리한다. `kepano/obsidian-skills`가 제공하는 `obsidian` CLI를 활용한다.

## Pre-flight Check

skill을 실행하기 전에 반드시 아래 검사를 순서대로 수행한다. 실패 시 해당 단계의 안내 메시지를 출력하고 중단한다.

### 1. Git 저장소 확인

```bash
git rev-parse --show-toplevel
```

- 실패 시: "현재 디렉토리가 git 저장소가 아닙니다. git 저장소에서 실행해주세요."

### 2. Obsidian 앱 설치 확인

```bash
test -d "/Applications/Obsidian.app"
```

- 실패 시: "Obsidian 앱이 설치되어 있지 않습니다. https://obsidian.md/download 에서 다운로드하세요."

### 3. Obsidian 앱 실행 및 CLI 확인

```bash
obsidian help
```

- 정상 응답이 없거나 "out of date" 경고만 나오면:
  - "Obsidian 앱을 실행한 후 다시 시도하세요."
  - 인스톨러 구버전 경고 시: "최신 인스톨러로 업데이트하세요: https://obsidian.md/download"

### 4. Vault 통신 확인

```bash
obsidian vault="{vault-name}" search query="test" limit=1
```

- 실패 시: "vault '{vault-name}'에 접근할 수 없습니다. Obsidian 앱에서 해당 vault가 열려 있는지 확인하세요."

## Vault 설정 읽기

1. `.claude/local-memory.json` 파일을 읽는다
2. `vault` 키에서 vault 이름을 가져온다
3. `directory` 키에서 vault 내 루트 디렉토리 이름을 가져온다
4. 파일이 없거나 필수 설정이 누락되면 사용자에게 물어본다 (AskUserQuestion 사용)
5. 사용자가 입력한 값을 `.claude/local-memory.json`에 저장한다

**설정 파일**: `.claude/local-memory.json` (전용 설정 파일, settings.local.json과 분리)

```json
{
  "vault": "MyVault",
  "directory": "claude-memory"
}
```

- `vault` (필수): Obsidian vault 이름
- `directory` (선택): vault 내 루트 디렉토리 이름 (기본값: `claude-memory`)

이후 모든 `obsidian` CLI 호출에 `vault="{vault-name}"` 파라미터를 전달하며, vault 내 저장 경로는 `{directory}/{repo-name}/` 하위에 구성한다.

## Repo Name 추출

현재 작업 디렉토리의 git repo name을 추출한다:

```bash
# 1차: GitHub remote에서 추출
git remote get-url origin 2>/dev/null | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\///'

# fallback: git root 디렉토리명
basename $(git rev-parse --show-toplevel)
```

추출된 repo name은 `{directory}/{repo-name}/` 경로에서 사용한다.

## Vault 폴더 구조 초기화

repo name이 확인되면 vault 내 폴더 구조를 준비한다:

```bash
# repo 루트 폴더에 인덱스 노트 생성 (없을 경우)
obsidian vault="{vault-name}" create name="{repo-name}" path="{directory}" content="---\ntype: repo-index\nrepo: {repo-name}\ntags:\n  - repo/{repo-name}\n---\n\n# {repo-name}\n\nGitHub repo 외부기억 인덱스.\n\n## Specs\n\n![[{directory}/{repo-name}/specs]]\n\n## Ideas\n\n![[{directory}/{repo-name}/ideas]]" silent
```

## Skill 조율

이 에이전트는 아래 skill들의 실행 컨텍스트를 제공한다:

- **sync-specs**: specs 문서를 vault에 동기화
- **save-idea**: 아이디어 메모를 vault에 저장

각 skill 실행 전에:
1. Pre-flight check를 수행한다
2. vault 이름과 repo name을 확인한다
3. 해당 정보를 skill에 전달한다
