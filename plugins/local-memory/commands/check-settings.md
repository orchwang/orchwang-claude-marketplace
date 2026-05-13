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

#### 1.5 Django 휴리스틱 (정보성)

현재 repo가 Django 프로젝트인지 가벼운 휴리스틱으로 점검한다. `[scripts]` django-command 카테고리 동기화 대상 존재 여부를 안내하기 위한 정보성 검사이며 에러로 간주하지 않는다.

```bash
find . -maxdepth 3 -name manage.py 2>/dev/null | head -1
```

- INFO (있음): "`[scripts]` Django 프로젝트가 감지되었습니다. `/sync-scripts --category django-command`로 management 명령을 동기화할 수 있습니다."
- INFO (없음): "`[scripts]` Django 프로젝트가 아닙니다. django-command 카테고리는 동기화 대상이 없습니다."

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

AskUserQuestion으로 백엔드를 물어본다. 어느 한 백엔드도 자동 적용하지 않고 항상 사용자의 명시 선택을 받는다 (기본값 무음 적용 금지).

- "스토리지 백엔드를 선택해주세요: obsidian / filesystem / git"
- 세 옵션을 동등 비중으로 제시한다 — "권장", "기본값" 라벨 사용 금지

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

설정이 완료되면 실제 연결을 테스트한다. `[specs]`, `[scripts]` 영역의 결과 메시지는 라벨 접두를 사용하여 분리 출력한다 (한 메시지에서 두 영역 혼합 금지).

#### backend = obsidian

기본 연결 확인:

```bash
obsidian vault="{vault-name}" search query="test" limit=1
```

- 성공: "vault '{vault-name}' 연결 확인 완료"
- 실패: 원인별 안내 메시지 출력

`[specs]` 헬스체크 — specs 트리에 임시 노트 생성·확인·삭제:

```bash
obsidian vault="{vault-name}" create name=".healthcheck-specs" path="{directory}/{repo-name}/specs" content="ok" overwrite silent
obsidian vault="{vault-name}" read name=".healthcheck-specs" path="{directory}/{repo-name}/specs"
obsidian vault="{vault-name}" delete name=".healthcheck-specs" path="{directory}/{repo-name}/specs"
```

- 성공: "[specs] specs 트리 쓰기/읽기 확인 완료"

`[scripts]` 헬스체크 — scripts 트리에 임시 노트 생성·확인·삭제:

```bash
obsidian vault="{vault-name}" create name=".healthcheck-scripts" path="{directory}/{repo-name}/scripts" content="ok" overwrite silent
obsidian vault="{vault-name}" read name=".healthcheck-scripts" path="{directory}/{repo-name}/scripts"
obsidian vault="{vault-name}" delete name=".healthcheck-scripts" path="{directory}/{repo-name}/scripts"
```

- 성공: "[scripts] scripts 트리 쓰기/읽기 확인 완료"

#### backend = filesystem

기본 연결 확인:

```bash
echo "test" > "{basePath}/.local-memory-test" && cat "{basePath}/.local-memory-test" && rm "{basePath}/.local-memory-test"
```

- 성공: "basePath '{basePath}' 읽기/쓰기 확인 완료"

`[specs]` 헬스체크:

```bash
mkdir -p "{basePath}/{directory}/{repo-name}/specs"
echo "ok" > "{basePath}/{directory}/{repo-name}/specs/.healthcheck.md"
cat "{basePath}/{directory}/{repo-name}/specs/.healthcheck.md"
rm "{basePath}/{directory}/{repo-name}/specs/.healthcheck.md"
```

- 성공: "[specs] specs 트리 쓰기/읽기 확인 완료"

`[scripts]` 헬스체크:

```bash
mkdir -p "{basePath}/{directory}/{repo-name}/scripts"
echo "ok" > "{basePath}/{directory}/{repo-name}/scripts/.healthcheck.md"
cat "{basePath}/{directory}/{repo-name}/scripts/.healthcheck.md"
rm "{basePath}/{directory}/{repo-name}/scripts/.healthcheck.md"
```

- 성공: "[scripts] scripts 트리 쓰기/읽기 확인 완료"

#### backend = git

filesystem 동일 시퀀스에 더해 git 상태 확인 (헬스체크 임시 파일은 커밋하지 않음 — 항상 삭제 후 종료):

```bash
echo "test" > "{basePath}/.local-memory-test" && cat "{basePath}/.local-memory-test" && rm "{basePath}/.local-memory-test"
mkdir -p "{basePath}/{directory}/{repo-name}/specs" "{basePath}/{directory}/{repo-name}/scripts"
echo "ok" > "{basePath}/{directory}/{repo-name}/specs/.healthcheck.md" && cat "$_" && rm "$_"
echo "ok" > "{basePath}/{directory}/{repo-name}/scripts/.healthcheck.md" && cat "$_" && rm "$_"
git -C "{basePath}" status
```

- 성공: "[specs] specs 트리 / [scripts] scripts 트리 / basePath 읽기·쓰기 및 git 저장소 확인 완료" (영역별 라벨 분리 출력)
- 실패: 원인별 안내 메시지 출력

### Step 5b: 마이그레이션 감사 (v2.0.0 → v2.1.0)

기존 사용자 데이터 호환을 위해 인덱스 노트·`scripts/` 트리·레거시 평면 트리 상태를 점검한다. 모든 항목은 정보성·진단성이며 자동 변경하지 않는다.

| 항목 | 검사 | 보강 명령 |
|------|------|----------|
| 인덱스 노트 존재 | EXISTS `{directory}/{repo-name}/{repo-name}.md` | (MISSING) `/sync-scripts` 또는 `/save-idea` 1회 실행 시 자동 생성 |
| 인덱스의 `## Scripts` 섹션 | READ 후 `^## Scripts\s*$` 라인 검출 | (MISSING) `/sync-scripts`(빈 호출 포함) 1회 실행 시 비파괴 append |
| `{directory}/{repo-name}/scripts/` 트리 | EXISTS `scripts/` | (MISSING) `/sync-scripts` 실행 시 자동 생성 |
| 레거시 루트 평면 트리(`django-commands/`) | filesystem/git 백엔드 한정: `test -d "{basePath}/django-commands"` | (INFO) `docs/migrations/datamaker-docs-django-commands.md` 가이드 참조 — 자동 변환 없음 |

출력 예시:

```
## 마이그레이션 감사
| 항목 | 상태 | 메시지 |
|------|------|--------|
| 인덱스 노트 | OK | {directory}/{repo}/{repo}.md |
| ## Scripts 섹션 | MISSING | /sync-scripts 1회 실행으로 비파괴 append |
| scripts/ 트리 | MISSING | /sync-scripts 실행 시 자동 생성 |
| 레거시 django-commands/ | INFO | 발견됨 — 가이드 참조 (자동 변환 없음) |
```

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
