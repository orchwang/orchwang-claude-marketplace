# Source Config Reference

`knowledge-librarian` 플러그인의 지식 소스 설정 스키마와 백엔드별 **read-only** 명령 매핑 레퍼런스.

> ⚠️ **read-only 불변식**: 본 플러그인은 지식 소스(`basePath` / `vault`)에 **어떤 파일도 생성·수정·삭제하지 않으며 git commit/push도 하지 않는다.** `local-memory`의 git 백엔드가 write(커밋/푸시)를 수행하는 것과 **정반대**다. 소스는 항상 읽기 전용이다.

## 설정 파일 — `.claude/knowledge-librarian.json`

`local-memory.json`과 완전히 분리된 전용 설정 파일이다.

```json
{
  "backend": "git",
  "indexPath": ".claude/knowledge-index.json",
  "sources": [
    {
      "name": "eng-wiki",
      "backend": "git",
      "basePath": "/Users/jongtaek.hwang/Projects/company-wiki",
      "roots": ["architecture/", "data-platform/", "runbooks/"],
      "include": ["**/*.md"],
      "exclude": ["**/_drafts/**", "**/archive/**"]
    },
    {
      "name": "obsidian-notes",
      "backend": "obsidian",
      "vault": "TeamVault",
      "roots": ["knowledge/"]
    }
  ]
}
```

### 필드

| 필드 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `backend` | 선택 | 전역 기본 backend (`obsidian` / `filesystem` / `git`) | `git` |
| `indexPath` | 선택 | 카탈로그 저장 경로(현재 repo 기준 상대경로) | `.claude/knowledge-index.json` |
| `sources[]` | 필수 | 지식 소스 배열 (1개 이상) | — |
| `sources[].name` | 필수 | 소스 식별자 (인덱스·검색 구분 키) | — |
| `sources[].backend` | 선택 | 소스별 backend (미지정 시 전역 상속) | 전역 `backend` |
| `sources[].basePath` | filesystem/git 필수 | 소스 저장소 루트 절대경로 | — |
| `sources[].vault` | obsidian 필수 | obsidian vault 이름 | — |
| `sources[].roots[]` | 선택 | 지식 대상 하위 경로 목록 (소스 루트 기준) | `[]`(소스 전체) |
| `sources[].include[]` | 선택 | 포함 글롭 | `["**/*.md"]` |
| `sources[].exclude[]` | 선택 | 제외 글롭 | `[]` |

> `readOnly`는 설정 항목으로 노출하지 않는다 — 소스는 **항상** read-only다.

## 백엔드별 read 매핑

`local-memory/references/backend-operations.md`의 READ 계열만 차용한다. **CREATE · commit · push 명령은 본 레퍼런스에 존재하지 않는다.**

| Operation | filesystem / git | obsidian |
|-----------|------------------|----------|
| SCAN (roots 하위 md 목록) | `find "{basePath}/{root}" -name "*.md" -type f` (+ include/exclude 필터) | `obsidian vault="{vault}" search query="path:{root}" limit={N}` |
| READ (문서 본문) | `cat "{basePath}/{path}"` | `obsidian vault="{vault}" read name="{name}" path="{path}"` |
| EXISTS (소스/루트 확인) | `test -d "{basePath}/{root}"` | `obsidian vault="{vault}" search query="path:{root}" limit=1` |
| MTIME / SIZE | `stat -f '%m %z' "{basePath}/{path}"` (darwin) / `stat -c '%Y %s'` (linux) | frontmatter/search 메타 근사 |

- **git 소스도 워킹트리를 그대로 읽는다** — checkout / pull / commit / push 를 수행하지 않는다.
- include / exclude 글롭은 SCAN 결과에 대해 플러그인이 후처리 필터링한다.

## Pre-flight (소스 접근성)

### filesystem / git
1. `test -d "{basePath}"` — 소스 루트 존재
2. `roots[]` 각각 `test -d "{basePath}/{root}"` — 없는 root는 경고 후 스킵(전체 실패 아님)
3. 쓰기 권한은 **검사하지 않는다** (read-only)

### obsidian
1. `obsidian help` — CLI 동작
2. `obsidian vault="{vault}" search query="test" limit=1` — vault 통신
3. `roots[]` 각각 search로 존재 근사 확인

## Jekyll 블로그 예시 (검증됨)

Jekyll은 포스트가 `_posts/` 하위에 카테고리별로 중첩되고, 생성물 `_site/`가 md를 중복 보유한다. `roots`를 `_posts/`로 한정하면 `_site/`가 자연히 배제된다(추가로 `exclude` 명시하여 이중 안전).

```json
{
  "backend": "git",
  "indexPath": ".claude/knowledge-index.json",
  "sources": [
    {
      "name": "blog",
      "backend": "git",
      "basePath": "/Users/jongtaek.hwang/Projects/private/orchwang.github.io",
      "roots": ["_posts/"],
      "include": ["**/*.md"],
      "exclude": ["**/_site/**", "**/_drafts/**"]
    }
  ]
}
```

- Jekyll frontmatter(`title` / `tags` / `categories` / `excerpt` / `series` / `published`)는 `references/index-format.md`의 파싱 규칙과 정합
- git 소스이지만 read-only — 블로그 워킹트리를 읽기만 함
