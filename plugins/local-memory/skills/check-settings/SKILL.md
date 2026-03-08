---
name: check-settings
description: local-memory 플러그인 사용에 필요한 설정 항목을 검토하고, 누락된 설정을 안내·제안한다. Use when the user mentions "설정 확인", "check settings", "setup", "local-memory 설정", or wants to configure the local-memory plugin.
---

# check-settings

local-memory 플러그인이 현재 repo 환경에서 정상 동작하기 위한 설정을 검토하고, 누락 항목을 안내·설정하는 skill.

## Input

`/check-settings` — 인자 없이 실행

## Process

### Step 1: 환경 검사

아래 항목을 순서대로 검사하여 결과를 수집한다. 각 항목은 OK / MISSING / WARNING 상태로 분류한다.

#### 1.1 Git 저장소

```bash
git rev-parse --show-toplevel 2>/dev/null
```

- OK: git 저장소 내에서 실행 중
- MISSING: git 저장소가 아님

#### 1.2 Repo name 감지

```bash
git remote get-url origin 2>/dev/null | sed 's/.*\/\(.*\)\.git/\1/' | sed 's/.*\///'
```

- OK: repo name 추출 성공
- WARNING: remote가 없음 (fallback으로 디렉토리명 사용 가능)

#### 1.3 Obsidian 앱 설치

```bash
test -d "/Applications/Obsidian.app"
```

- OK: 설치됨
- MISSING: 미설치

#### 1.4 Obsidian CLI 동작

```bash
obsidian help 2>&1
```

- OK: 정상 응답
- WARNING: "out of date" 경고 (인스톨러 업데이트 필요)
- MISSING: 응답 없음 (앱 미실행)

#### 1.5 obsidian-skills 플러그인

시스템에 `obsidian:obsidian-cli` skill이 등록되어 있는지 확인한다.

- OK: skill 사용 가능
- MISSING: 미설치

### Step 2: settings.local.json 검토

`.claude/settings.local.json` 파일을 읽어 `local-memory` 설정 항목을 검사한다.

#### 2.1 파일 존재 여부

- OK: 파일 존재
- MISSING: 파일 없음 → 생성 필요

#### 2.2 `local-memory.vault`

- OK: 값이 설정됨
- MISSING: 미설정

#### 2.3 `local-memory.directory`

- OK: 값이 설정됨
- MISSING: 미설정 (기본값 `claude-memory` 사용 가능)

### Step 3: 결과 리포트 출력

검사 결과를 테이블로 출력한다:

```
local-memory 설정 검토 결과

## 환경
| 항목 | 상태 | 값/메시지 |
|------|------|-----------|
| Git 저장소 | OK | /path/to/repo |
| Repo name | OK | orchwang-claude-marketplace |
| Obsidian 앱 | OK | /Applications/Obsidian.app |
| Obsidian CLI | WARNING | 인스톨러 업데이트 권장 |
| obsidian-skills | OK | obsidian:obsidian-cli 사용 가능 |

## 설정 (.claude/settings.local.json)
| 항목 | 상태 | 값/메시지 |
|------|------|-----------|
| local-memory.vault | MISSING | 설정 필요 |
| local-memory.directory | MISSING | 기본값 "claude-memory" 사용 |
```

### Step 4: 누락 항목 설정 제안

MISSING 상태인 설정 항목이 있으면 사용자에게 설정을 제안한다.

#### vault 미설정 시

AskUserQuestion으로 vault 이름을 물어본다:

- "사용할 Obsidian vault 이름을 입력해주세요."
- Obsidian CLI가 동작 중이면 `obsidian vaults` 등으로 사용 가능한 vault 목록을 제공한다 (가능한 경우)

#### directory 미설정 시

AskUserQuestion으로 directory 이름을 물어본다:

- "vault 내 루트 디렉토리 이름을 지정해주세요."
- 옵션: `claude-memory` (기본값 권장) / 직접 입력

#### 설정 저장

사용자가 입력한 값을 `.claude/settings.local.json`에 저장한다. 기존 설정이 있으면 `local-memory` 키만 추가/병합한다.

```json
{
  "local-memory": {
    "vault": "{사용자 입력}",
    "directory": "{사용자 입력 또는 기본값}"
  }
}
```

### Step 5: Vault 연결 테스트

설정이 완료되면 실제 vault 연결을 테스트한다:

```bash
obsidian vault="{vault-name}" search query="test" limit=1
```

- 성공: "vault '{vault-name}' 연결 확인 완료"
- 실패: 원인별 안내 메시지 출력

### Step 6: 최종 요약

```
설정 완료!

  vault: {vault-name}
  directory: {directory}
  repo: {repo-name}
  저장 경로: vault/{directory}/{repo-name}/

사용 가능한 명령어:
  /sync-specs [task-name]  — specs 문서를 vault에 동기화
  /save-idea "제목"        — 아이디어 메모를 vault에 저장
```

MISSING 항목이 남아있으면 해결이 필요한 항목 목록을 다시 표시한다.
