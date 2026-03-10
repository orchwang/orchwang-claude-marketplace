---
name: check-settings
description: local-memory 플러그인 환경 및 설정을 검토하고, 누락된 항목을 대화형으로 설정한다.
---

# check-settings

local-memory 플러그인이 현재 repo 환경에서 정상 동작하기 위한 설정을 검토하고, 누락 항목을 안내·설정하는 command.

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

#### 1.3 백엔드 확인

`.claude/local-memory.json`에서 `backend` 값을 읽는다. 없으면 기본값 `"obsidian"`.

#### 1.4 백엔드별 환경 검사

##### backend = obsidian

**1.4a Obsidian 앱 설치**

```bash
test -d "/Applications/Obsidian.app"
```

- OK: 설치됨
- MISSING: 미설치

**1.4b Obsidian CLI 동작**

```bash
obsidian help 2>&1
```

- OK: 정상 응답
- WARNING: "out of date" 경고 (인스톨러 업데이트 필요)
- MISSING: 응답 없음 (앱 미실행)

**1.4c obsidian-skills 플러그인**

시스템에 `obsidian:obsidian-cli` skill이 등록되어 있는지 확인한다.

- OK: skill 사용 가능
- MISSING: 미설치

##### backend = filesystem

**1.4a basePath 존재**

```bash
test -d "{basePath}"
```

- OK: 디렉토리 존재
- MISSING: 디렉토리 없음

**1.4b 쓰기 권한**

```bash
test -w "{basePath}"
```

- OK: 쓰기 가능
- MISSING: 쓰기 권한 없음

##### backend = git

**1.4a basePath 존재**

```bash
test -d "{basePath}"
```

- OK: 디렉토리 존재
- MISSING: 디렉토리 없음

**1.4b 쓰기 권한**

```bash
test -w "{basePath}"
```

- OK: 쓰기 가능
- MISSING: 쓰기 권한 없음

**1.4c git 저장소 확인**

```bash
git -C "{basePath}" rev-parse --is-inside-work-tree
```

- OK: git 저장소
- MISSING: git 저장소 아님

### Step 2: local-memory.json 검토

`.claude/local-memory.json` 파일을 읽어 설정 항목을 검사한다.

#### 2.1 파일 존재 여부

- OK: 파일 존재
- MISSING: 파일 없음 → 생성 필요

#### 2.2 `backend`

- OK: 유효한 값 (`obsidian` / `filesystem` / `git`)
- MISSING: 미설정 (기본값 `obsidian` 사용)

#### 2.3 `vault` (obsidian 백엔드만)

- OK: 값이 설정됨
- MISSING: 미설정

#### 2.4 `basePath` (filesystem / git 백엔드만)

- OK: 값이 설정됨
- MISSING: 미설정

#### 2.5 `directory`

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
| Repo name | OK | my-repo |
| Backend | OK | filesystem |
```

backend = obsidian인 경우:

```
| Obsidian 앱 | OK | /Applications/Obsidian.app |
| Obsidian CLI | WARNING | 인스톨러 업데이트 권장 |
| obsidian-skills | OK | obsidian:obsidian-cli 사용 가능 |
```

backend = filesystem인 경우:

```
| basePath 존재 | OK | /home/user/claude-memory-store |
| 쓰기 권한 | OK | 쓰기 가능 |
```

backend = git인 경우:

```
| basePath 존재 | OK | /home/user/claude-memory-store |
| 쓰기 권한 | OK | 쓰기 가능 |
| git 저장소 | OK | git 저장소 확인됨 |
```

설정 항목:

```
## 설정 (.claude/local-memory.json)
| 항목 | 상태 | 값/메시지 |
|------|------|-----------|
| backend | OK | filesystem |
| basePath | OK | /home/user/claude-memory-store |
| directory | MISSING | 기본값 "claude-memory" 사용 |
```

### Step 4: 누락 항목 설정 제안

MISSING 상태인 설정 항목이 있으면 사용자에게 설정을 제안한다.

#### backend 미설정 시

AskUserQuestion으로 백엔드를 물어본다:

- "스토리지 백엔드를 선택해주세요: obsidian / filesystem / git"

#### vault 미설정 시 (obsidian 백엔드)

AskUserQuestion으로 vault 이름을 물어본다:

- "사용할 Obsidian vault 이름을 입력해주세요."
- Obsidian CLI가 동작 중이면 `obsidian vaults` 등으로 사용 가능한 vault 목록을 제공한다 (가능한 경우)

#### basePath 미설정 시 (filesystem / git 백엔드)

AskUserQuestion으로 basePath를 물어본다:

- "저장소 루트 경로를 입력해주세요. (절대 경로)"

#### directory 미설정 시

AskUserQuestion으로 directory 이름을 물어본다:

- "하위 디렉토리 이름을 지정해주세요."
- 옵션: `claude-memory` (기본값 권장) / 직접 입력

#### 설정 저장

사용자가 입력한 값을 `.claude/local-memory.json`에 저장한다. 파일이 없으면 새로 생성한다.

```json
{
  "backend": "{사용자 입력}",
  "vault": "{obsidian인 경우}",
  "basePath": "{filesystem/git인 경우}",
  "directory": "{사용자 입력 또는 기본값}"
}
```

### Step 5: 연결 테스트

설정이 완료되면 실제 연결을 테스트한다.

#### backend = obsidian

```bash
obsidian vault="{vault-name}" search query="test" limit=1
```

- 성공: "vault '{vault-name}' 연결 확인 완료"
- 실패: 원인별 안내 메시지 출력

#### backend = filesystem

테스트 파일을 생성·읽기·삭제한다:

```bash
echo "test" > "{basePath}/.local-memory-test" && cat "{basePath}/.local-memory-test" && rm "{basePath}/.local-memory-test"
```

- 성공: "basePath '{basePath}' 읽기/쓰기 확인 완료"
- 실패: 원인별 안내 메시지 출력

#### backend = git

filesystem 테스트 + git 상태 확인:

```bash
echo "test" > "{basePath}/.local-memory-test" && cat "{basePath}/.local-memory-test" && rm "{basePath}/.local-memory-test"
git -C "{basePath}" status
```

- 성공: "basePath '{basePath}' 읽기/쓰기 및 git 저장소 확인 완료"
- 실패: 원인별 안내 메시지 출력

### Step 6: 최종 요약

```
설정 완료!

  backend: {backend}
  vault: {vault-name}          # obsidian인 경우
  basePath: {basePath}         # filesystem/git인 경우
  directory: {directory}
  repo: {repo-name}
  저장 경로: {backend별 경로}

사용 가능한 명령어:
  /sync-specs [task-name]  — specs 문서를 저장소에 동기화
  /save-idea "제목"        — 아이디어 메모를 저장소에 저장
```

MISSING 항목이 남아있으면 해결이 필요한 항목 목록을 다시 표시한다.
