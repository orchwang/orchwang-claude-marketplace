# local-memory

GitHub repo 단위 외부기억(specs · scripts · ideas)을 선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 Claude Code 플러그인입니다.

## 개요

Claude Code 작업 중 생성되는 컨텍스트(specs 문서, 스크립트, 아이디어 메모 등)를 외부 저장소에 자동으로 동기화합니다. repo name을 기준으로 폴더를 구조화하여 프로젝트별 외부기억을 관리합니다.

백엔드(obsidian / filesystem / git)를 선택할 수 있으며, `datamaker-docs` 같은 git 저장소를 외부기억으로 그대로 사용할 수도 있습니다.

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

`.claude/local-memory.json`에 백엔드와 저장 경로를 지정합니다. 세 백엔드를 동등하게 지원합니다.

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
  "basePath": "/Users/jongtaek.hwang/Projects/datamaker-docs",
  "directory": "claude-memory",
  "gitAutoCommit": true,
  "gitRemote": "origin"
}
```

> 실제 운영 예시 — `datamaker-docs`를 외부기억으로 활용. `directory`를 비우거나 `"."`로 두면 저장소 루트에 직접 적재할 수도 있습니다.

### obsidian

```json
{
  "backend": "obsidian",
  "vault": "MyVault",
  "directory": "claude-memory"
}
```

> Note: `backend` 미설정 시 동작 호환성을 위해 `obsidian`이 사용됩니다. 신규 사용자는 `/check-settings`로 명시적으로 선택하세요.

### 설정 항목

| 항목 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `backend` | 선택 | `obsidian` / `filesystem` / `git` | `obsidian` ¹ |
| `vault` | obsidian | obsidian vault 이름 | — |
| `basePath` | filesystem / git | 저장소 루트 절대 경로 | — |
| `directory` | 선택 | 하위 디렉토리 이름 | `claude-memory` |
| `gitAutoCommit` | 선택 | git 백엔드 자동 커밋 | `true` |
| `gitRemote` | 선택 | git 백엔드 push 대상 remote | `origin` |

¹ 기본값은 호환성용. `/check-settings`로 명시 선택을 권장합니다.

> `/check-settings`를 실행하면 설정을 대화형으로 안내받을 수 있습니다.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/check-settings` | 환경 및 설정 검토, 누락 항목 안내, 마이그레이션 감사 |
| `/sync-specs [task-name]` | specs 문서를 저장소에 동기화 |
| `/sync-scripts [path|glob] [--category bash\|makefile\|django-command\|all]` | 저장소 스크립트를 외부기억에 동기화 |
| `/save-idea "제목" [--tag tag1,tag2]` | 아이디어 메모를 저장소에 저장 |

## Scripts Management

`/sync-scripts`는 저장소의 스크립트를 외부기억의 `scripts/` 트리에 동기화합니다.

| 카테고리 | 인식 규칙 | 저장 위치 |
|---------|---------|---------|
| bash | `scripts/**/*.sh`, `bin/**/*.sh`, 실행권한 `*.sh` | `{repo}/scripts/bash/` |
| makefile | `Makefile`, `*/Makefile`, `*.mk` | `{repo}/scripts/makefile/` |
| django-command | `**/management/commands/*.py` (제외: `__init__.py`) | `{repo}/scripts/django-command/{app}/` |

> 인식 규칙과 자연어 의도 매핑 전문은 [`references/script-sources.md`](./references/script-sources.md)를 참조하세요.
>
> spec 문서 동기화는 `/sync-specs`를 사용하세요 — 두 영역은 별도 skill로 분리되어 있습니다.

## 에이전트

| 에이전트 | 설명 |
|----------|------|
| `repo-memory` | repo 컨텍스트 관리 (사전 검사, repo 감지, 저장소 폴더 구조화, scope 라우팅, 인덱스 노트 비파괴 병합) |

## 폴더 구조

### obsidian

```
vault/
  {directory}/
    {repo-name}/
      {repo-name}.md          # 인덱스 (## Specs / ## Scripts / ## Ideas)
      specs/
        {task-name}/
          {task-name}-requirements.md
          {task-name}-specs.md
          {task-name}-plans.md
      scripts/
        bash/
        makefile/
        django-command/
          {app}/
      ideas/
        {idea-slug}.md
```

### filesystem / git

```
{basePath}/
  {directory}/
    {repo-name}/
      {repo-name}.md          # 인덱스 (## Specs / ## Scripts / ## Ideas)
      specs/
        {task-name}/
          {task-name}-requirements.md
          {task-name}-specs.md
          {task-name}-plans.md
      scripts/
        bash/
        makefile/
        django-command/
          {app}/
      ideas/
        {idea-slug}.md
```

## v2.0.0 → v2.1.0 업그레이드

본 업데이트는 기존 데이터를 손상시키지 않습니다.

- 기존 `.claude/local-memory.json` 그대로 동작합니다
- 기존 `{directory}/{repo}/specs/`, `ideas/`, 인덱스 노트는 보존됩니다
- 신규 `scripts/` 트리와 인덱스 `## Scripts` 섹션은 처음 `/sync-scripts`를 실행할 때 자동 생성됩니다
- 진단: `/check-settings`의 "마이그레이션 감사" 절을 확인하세요
- `datamaker-docs`의 루트 `django-commands/` 트리를 사용 중이라면 별도 가이드 참조: [`docs/migrations/datamaker-docs-django-commands.md`](../../docs/migrations/datamaker-docs-django-commands.md)
- 다운그레이드 안전성: 추가된 `## Scripts` 섹션은 v2.0.0에서도 단순 마크다운으로 무해합니다

## 라이선스

MIT
