# Specs: Abstraction for local-memory plugin

> Created: 2026-03-09
> Status: Complete
> Requirements: [requirements.md](./requirements.md)

## Overview

local-memory 플러그인의 스토리지 백엔드를 추상화하여 obsidian, filesystem, git 세 가지 백엔드를 설정으로 선택할 수 있게 한다. 핵심 연산 4가지(CREATE, READ, SEARCH, EXISTS)를 백엔드별로 매핑하고, 모든 skill/agent/command가 이 매핑을 참조하도록 한다.

## Technical Specifications

### Config Schema

`.claude/local-memory.json` 확장:

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

| 필드 | 타입 | 필수 조건 | 기본값 |
|------|------|-----------|--------|
| `backend` | `"obsidian" \| "filesystem" \| "git"` | 선택 | `"obsidian"` |
| `vault` | string | obsidian 필수 | — |
| `basePath` | string (절대경로) | filesystem/git 필수 | — |
| `directory` | string | 선택 | `"claude-memory"` |
| `gitAutoCommit` | boolean | 선택 | `true` |
| `gitRemote` | string | 선택 | `"origin"` |

### Backend Operations Mapping

| Operation | obsidian | filesystem / git |
|-----------|----------|-----------------|
| CREATE | `obsidian vault="{vault}" create name="{name}" path="{path}" content="..." overwrite silent` | `mkdir -p "{basePath}/{path}" && cat > "{basePath}/{path}/{name}.md"` |
| READ | `obsidian vault="{vault}" read name="{name}" path="{path}"` | `cat "{basePath}/{path}/{name}.md"` |
| SEARCH | `obsidian vault="{vault}" search query="path:{path}" limit=N` | `find "{basePath}/{path}" -name "*.md" -type f` |
| EXISTS | `obsidian vault="{vault}" search query="path:{path}/{name}" limit=1` | `test -f "{basePath}/{path}/{name}.md"` |

git 백엔드 = filesystem + 쓰기 후 `git add -A && git commit -m "..." && git push {gitRemote}`

### Pre-flight Check 분기

| 검사 항목 | obsidian | filesystem | git |
|-----------|----------|------------|-----|
| Git repo | O | O | O |
| Obsidian 앱 | O | — | — |
| Obsidian CLI | O | — | — |
| Vault 통신 | O | — | — |
| basePath 존재 | — | O | O |
| 쓰기 권한 | — | O | O |
| git 저장소 확인 | — | — | O |

### 링크 형식

- obsidian: `![[{directory}/{repo-name}/specs]]` (wikilinks)
- filesystem/git: `[specs](./{repo-name}/specs/)` (표준 마크다운)

## Architecture

### 파일 구조

```
plugins/local-memory/
  references/
    backend-operations.md    # 백엔드별 명령어 레퍼런스 (NEW)
  agents/repo-memory/
    AGENT.md                 # 백엔드 분기 추가
  commands/
    check-settings.md        # 백엔드별 검사 추가
  skills/
    sync-specs/SKILL.md      # 백엔드별 저장 추가
    save-idea/SKILL.md       # 백엔드별 저장/검색 추가
  plugin.json                # v2.0.0 버전업
  README.md                  # Backend Configuration 섹션 추가
```

### 데이터 흐름

1. skill/command 실행 → repo-memory 에이전트 호출
2. 에이전트가 `.claude/local-memory.json`에서 `backend` 읽기
3. 백엔드별 Pre-flight check 수행
4. `references/backend-operations.md` 참조하여 적절한 명령 실행

## Error Handling

- `backend` 값이 유효하지 않은 경우: "지원하지 않는 백엔드입니다. obsidian / filesystem / git 중 선택하세요."
- `basePath` 미설정 (filesystem/git): "basePath가 설정되지 않았습니다. `.claude/local-memory.json`에 basePath를 추가하세요."
- `basePath` 디렉토리 없음: "basePath '{basePath}'가 존재하지 않습니다."
- git 저장소 아님 (git 백엔드): "basePath '{basePath}'가 git 저장소가 아닙니다."

## Dependencies

- **obsidian 백엔드**: `kepano/obsidian-skills` 플러그인 (기존과 동일)
- **filesystem 백엔드**: 추가 의존성 없음
- **git 백엔드**: git CLI

## Open Questions

- (해결됨) 백엔드 간 마이그레이션 도구 필요 여부 → Out of Scope로 결정
