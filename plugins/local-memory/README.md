# local-memory

GitHub repo 단위 외부기억을 Obsidian vault에 저장·관리하는 Claude Code 플러그인입니다.

## 개요

Claude Code 작업 중 생성되는 컨텍스트(specs 문서, 아이디어 메모 등)를 Obsidian vault에 자동으로 동기화합니다. repo name을 기준으로 폴더를 구조화하여 프로젝트별 외부기억을 관리합니다.

## 요구 사항

- **Obsidian 앱** v1.12+ (최신 인스톨러 권장)
- **kepano/obsidian-skills** Claude Code 플러그인

## 설치

```bash
# 1. 의존성 설치 (필수)
/plugin install obsidian@kepano/obsidian-skills

# 2. local-memory 설치
/plugin install local-memory@orchwang-marketplace
```

## Vault 설정

`.claude/local-memory.json`에 대상 vault를 지정합니다:

```json
{
  "vault": "MyVault",
  "directory": "claude-memory"
}
```

- `vault` (필수): Obsidian vault 이름
- `directory` (선택): vault 내 루트 디렉토리 이름 (기본값: `claude-memory`)

> `/check-settings`를 실행하면 설정을 대화형으로 안내받을 수 있습니다.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/check-settings` | 환경 및 설정 검토, 누락 항목 안내 |
| `/sync-specs [task-name]` | specs 문서를 Obsidian vault에 동기화 |
| `/save-idea "제목" [--tag tag1,tag2]` | 아이디어 메모를 vault에 저장 |

## 에이전트

| 에이전트 | 설명 |
|----------|------|
| `repo-memory` | repo 컨텍스트 관리 (사전 검사, repo 감지, vault 폴더 구조화) |

## Vault 폴더 구조

```
vault/
  {directory}/              # 예: claude-memory
    {repo-name}/
      specs/
        {task-name}/
          requirements.md
          specs.md
          plans.md
      ideas/
        {idea-slug}.md
```

## 라이선스

MIT
