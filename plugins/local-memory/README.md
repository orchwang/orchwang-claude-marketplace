# local-memory

GitHub repo 단위 외부기억을 Obsidian vault 또는 로컬 파일시스템에 저장·관리하는 Claude Code 플러그인입니다.

## 개요

Claude Code 작업 중 생성되는 컨텍스트(specs 문서, 아이디어 메모 등)를 저장소에 자동으로 동기화합니다. repo name을 기준으로 폴더를 구조화하여 프로젝트별 외부기억을 관리합니다.

스토리지 백엔드를 선택할 수 있어 Obsidian이 없는 서버 환경에서도 사용할 수 있습니다.

## 요구 사항

### 공통
- **Git** — 현재 디렉토리가 git 저장소여야 합니다

### obsidian 백엔드
- **Obsidian 앱** v1.12+ (최신 인스톨러 권장)
- **kepano/obsidian-skills** Claude Code 플러그인

### filesystem 백엔드
- 쓰기 가능한 디렉토리 경로

### git 백엔드
- 쓰기 가능한 git 저장소 경로

## 설치

```bash
# local-memory 설치
/plugin install local-memory@orchwang-marketplace

# obsidian 백엔드 사용 시 의존성 설치
/plugin install obsidian@kepano/obsidian-skills
```

## Backend 설정

`.claude/local-memory.json`에 백엔드와 저장 경로를 지정합니다.

### obsidian (기본값)

```json
{
  "backend": "obsidian",
  "vault": "MyVault",
  "directory": "claude-memory"
}
```

### filesystem

```json
{
  "backend": "filesystem",
  "basePath": "/home/user/claude-memory-store",
  "directory": "claude-memory"
}
```

### git

```json
{
  "backend": "git",
  "basePath": "/home/user/claude-memory-repo",
  "directory": "claude-memory",
  "gitAutoCommit": true,
  "gitRemote": "origin"
}
```

### 설정 항목

| 항목 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `backend` | 선택 | `obsidian` / `filesystem` / `git` | `obsidian` |
| `vault` | obsidian | Obsidian vault 이름 | — |
| `basePath` | filesystem/git | 저장소 루트 절대 경로 | — |
| `directory` | 선택 | 하위 디렉토리 이름 | `claude-memory` |
| `gitAutoCommit` | 선택 | git 백엔드 자동 커밋 | `true` |
| `gitRemote` | 선택 | git 백엔드 push 대상 remote | `origin` |

> `/check-settings`를 실행하면 설정을 대화형으로 안내받을 수 있습니다.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/check-settings` | 환경 및 설정 검토, 누락 항목 안내 |
| `/sync-specs [task-name]` | specs 문서를 저장소에 동기화 |
| `/save-idea "제목" [--tag tag1,tag2]` | 아이디어 메모를 저장소에 저장 |

## 에이전트

| 에이전트 | 설명 |
|----------|------|
| `repo-memory` | repo 컨텍스트 관리 (사전 검사, repo 감지, 저장소 폴더 구조화) |

## 폴더 구조

### obsidian

```
vault/
  {directory}/
    {repo-name}/
      specs/
        {task-name}/
          {task-name}-requirements.md
          {task-name}-specs.md
          {task-name}-plans.md
      ideas/
        {idea-slug}.md
```

### filesystem / git

```
{basePath}/
  {directory}/
    {repo-name}/
      {repo-name}.md          # 인덱스
      specs/
        {task-name}/
          {task-name}-requirements.md
          {task-name}-specs.md
          {task-name}-plans.md
      ideas/
        {idea-slug}.md
```

## 라이선스

MIT
