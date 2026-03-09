# Backend Operations Reference

local-memory 플러그인의 스토리지 백엔드별 명령어 레퍼런스.

## 설정 읽기

`.claude/local-memory.json`에서 아래 필드를 읽는다:

- `backend`: `"obsidian"` (기본값) | `"filesystem"` | `"git"`
- `vault`: Obsidian vault 이름 (obsidian 백엔드 필수)
- `basePath`: 저장소 루트 절대 경로 (filesystem/git 백엔드 필수)
- `directory`: 하위 디렉토리 이름 (기본값: `claude-memory`)
- `gitAutoCommit`: git 백엔드에서 자동 커밋 여부 (기본값: `true`)
- `gitRemote`: git 백엔드에서 push 대상 remote (기본값: `"origin"`)

## Operations

### CREATE — 파일 생성/덮어쓰기

#### obsidian

```bash
obsidian vault="{vault}" create name="{name}" path="{path}" content="{content}" overwrite silent
```

#### filesystem / git

```bash
mkdir -p "{basePath}/{path}" && cat > "{basePath}/{path}/{name}.md" << 'CONTENT_EOF'
{content}
CONTENT_EOF
```

git 백엔드인 경우 쓰기 후 커밋:

```bash
cd "{basePath}" && git add -A && git commit -m "local-memory: update {path}/{name}.md" && git push {gitRemote}
```

> git 백엔드에서 여러 파일을 연속 저장하는 경우, 개별 커밋 대신 모든 파일 쓰기 완료 후 한 번만 커밋+push 한다.

---

### READ — 파일 읽기

#### obsidian

```bash
obsidian vault="{vault}" read name="{name}" path="{path}"
```

#### filesystem / git

```bash
cat "{basePath}/{path}/{name}.md"
```

---

### SEARCH — 경로 내 파일 목록 조회

#### obsidian

```bash
obsidian vault="{vault}" search query="path:{path}" limit={N}
```

#### filesystem / git

```bash
find "{basePath}/{path}" -name "*.md" -type f
```

---

### EXISTS — 파일 존재 여부 확인

#### obsidian

```bash
obsidian vault="{vault}" search query="path:{path}/{name}" limit=1
```

#### filesystem / git

```bash
test -f "{basePath}/{path}/{name}.md"
```

---

## Pre-flight Check (백엔드별)

### obsidian

1. Obsidian 앱 설치 확인: `test -d "/Applications/Obsidian.app"`
2. Obsidian CLI 동작 확인: `obsidian help`
3. Vault 통신 확인: `obsidian vault="{vault}" search query="test" limit=1`

### filesystem

1. `basePath` 존재 확인: `test -d "{basePath}"`
2. 쓰기 권한 확인: `test -w "{basePath}"`

### git

1. `basePath` 존재 확인: `test -d "{basePath}"`
2. 쓰기 권한 확인: `test -w "{basePath}"`
3. git 저장소 확인: `git -C "{basePath}" rev-parse --is-inside-work-tree`

## 링크 형식

- **obsidian**: Obsidian wikilinks 사용 — `![[{path}]]`
- **filesystem / git**: 표준 마크다운 링크 사용 — `[{name}]({path}/{name}.md)`
