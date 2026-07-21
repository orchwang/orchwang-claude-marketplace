# Specs: knowledge-librarian plugin

> Created: 2026-07-21
> Updated: 2026-07-21
> Status: Draft
> Requirements: [requirements.md](./requirements.md)

## Overview

requirements.md의 10개 FR을 기술 사양으로 구체화한다. 핵심 설계 결정:

1. **read-only 파이프라인** — 소스는 READ/SEARCH/EXISTS만 사용하고 CREATE/커밋 경로를 갖지 않는다. `local-memory`의 write 파이프라인과 코드/문서 수준에서 분리한다.
2. **인덱스는 로컬 산출물** — 카탈로그는 현재 repo의 `.claude/knowledge-index.json`(또는 `indexPath`)에 저장한다. 소스 저장소에는 어떤 파일도 쓰지 않는다.
3. **indexer → dispatcher 2단 역할** — `librarian` 에이전트가 (a) 인덱싱·검색(indexer)과 (b) 전문가 서브에이전트 위임(dispatcher)을 모두 수행한다. 위임은 Agent 도구로 실재 에이전트를 호출한다.
4. **backend 추상화 재사용** — `local-memory/references/backend-operations.md`의 READ/SEARCH/EXISTS 매핑을 그대로 차용하되 CREATE 계열은 제외한 read-only 변형을 신규 레퍼런스로 둔다.
5. **다중 소스 + scope** — `sources[]`와 `--source` 인자로 소스 단위 스코핑을 제공한다.
6. **설정·명령 격리** — `.claude/knowledge-librarian.json` 및 `knowledge-*` 명령 접두로 `local-memory`와 어휘·라우팅을 분리한다.

## Technical Specifications

### 플러그인 레이아웃

```
plugins/knowledge-librarian/
  plugin.json
  README.md
  agents/
    librarian/
      AGENT.md
  commands/
    knowledge-settings.md
  skills/
    knowledge-index/
      SKILL.md
    knowledge-search/
      SKILL.md
    knowledge-ask/
      SKILL.md
  references/
    source-config.md        # 설정 스키마 · backend read 매핑 · read-only 보장
    index-format.md         # 카탈로그 스키마 · staleness 규칙
    dispatch-contract.md    # 전문가 서브에이전트 위임 계약
```

### 설정 스키마 — `.claude/knowledge-librarian.json`

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

| 필드 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `backend` | 선택 | 전역 기본 backend (`obsidian`/`filesystem`/`git`) | `git` |
| `indexPath` | 선택 | 카탈로그 저장 경로(현재 repo 기준) | `.claude/knowledge-index.json` |
| `sources[]` | 필수 | 지식 소스 배열 (1개 이상) | — |
| `sources[].name` | 필수 | 소스 식별자 (인덱스·검색 구분 키) | — |
| `sources[].backend` | 선택 | 소스별 backend (미지정 시 전역 상속) | 전역 `backend` |
| `sources[].basePath` | filesystem/git 필수 | 소스 저장소 루트 절대경로 | — |
| `sources[].vault` | obsidian 필수 | obsidian vault 이름 | — |
| `sources[].roots[]` | 선택 | 지식 대상 하위 경로 목록 | `[]`(소스 전체) |
| `sources[].include[]` | 선택 | 포함 글롭 | `["**/*.md"]` |
| `sources[].exclude[]` | 선택 | 제외 글롭 | `[]` |

> `readOnly`는 설정 항목으로 노출하지 않는다 — 소스는 **항상** read-only다 (FR-5).

#### 검증 예시 — Jekyll 블로그(`orchwang.github.io`)

실측으로 확인한 설정 예시. Jekyll 블로그는 포스트가 `_posts/` 하위에 카테고리별로 중첩되어 있고, `_site/`(생성물)를 `roots` 스코핑으로 자연히 제외한다.

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

- `_posts/` 212개 포스트, frontmatter 100% 일관(`title`/`tags`/`categories`/`excerpt`/`date`/`published`, 63%는 `series`) → 파싱 규칙과 정합
- `roots: ["_posts/"]`이 Jekyll 생성물 `_site/`의 md 중복을 배제 (추가로 `exclude`에 명시하여 이중 안전)
- `published: false` 초안은 인덱싱 제외 규칙으로 자동 필터
- git 소스이지만 read-only — 블로그 워킹트리를 읽기만 하고 커밋/푸시하지 않음 (FR-5)

### 인덱스(카탈로그) 스키마 — `index-format.md`

`indexPath`에 저장되는 JSON:

```json
{
  "generatedAt": "2026-07-21T10:00:00+09:00",
  "sources": {
    "eng-wiki": { "docCount": 128, "roots": ["architecture/", "..."] }
  },
  "entries": [
    {
      "source": "eng-wiki",
      "path": "data-platform/lakehouse-design.md",
      "title": "Lakehouse 설계 원칙",
      "headings": ["배경", "스토리지 레이어", "Iceberg 테이블 규약"],
      "tags": ["data-platform", "iceberg", "architecture"],
      "categories": ["Technology", "Data-Engineering"],
      "series": "data-engineering-101",
      "summary": "레이크하우스 도입 시 스토리지·테이블 포맷 결정 근거를 기술한다.",
      "size": 8241,
      "mtime": "2026-07-10T14:22:00+09:00"
    }
  ]
}
```

- **엔트리 파싱 순서**: frontmatter → 첫 H1 → H2/H3 수집 → 첫 문단(summary)
- **title 우선순위**: frontmatter `title` > 첫 H1 > 파일명(확장자 제거)
- **summary 우선순위**: frontmatter `summary` > `description` > `excerpt`(Jekyll 관례) > 첫 비어있지 않은 문단(최대 280자)
- **facet 필드**: frontmatter `tags` → `tags[]`, `categories` → `categories[]`, `series` → `series`(문자열, 있을 때만). 셋 다 검색 랭킹 가중 대상
- **published 필터**: frontmatter `published: false`(Jekyll 초안)인 문서는 인덱스에서 제외한다 (기본 동작)
- **staleness 판정**: 임의의 소스 파일 `mtime` > `generatedAt`이면 stale (FR-8)
- **증분 갱신**: 기존 엔트리의 `size`/`mtime`과 현재 파일 비교 → 변경/신규만 재파싱, 삭제분 제거

### Backend read 매핑 — `source-config.md`

`local-memory/references/backend-operations.md`의 read 계열만 차용한다. **CREATE·commit·push 명령은 본 레퍼런스에 존재하지 않는다.**

| Operation | filesystem / git | obsidian |
|-----------|------------------|----------|
| SCAN (roots 하위 md 목록) | `find "{basePath}/{root}" -name "*.md" -type f`(+ include/exclude 필터) | `obsidian vault="{vault}" search query="path:{root}" limit={N}` |
| READ (문서 본문) | `cat "{basePath}/{path}"` | `obsidian vault="{vault}" read name="{name}" path="{path}"` |
| EXISTS (소스/루트 확인) | `test -d "{basePath}/{root}"` | `obsidian vault="{vault}" search query="path:{root}" limit=1` |
| MTIME/SIZE | `stat -f '%m %z' "{basePath}/{path}"` (darwin) | frontmatter/search 메타 활용 (근사) |

> git 소스도 워킹트리를 `find`/`cat`으로 그대로 읽는다. checkout/pull/commit을 수행하지 않는다 (FR-5, FR-6).

### `librarian` 에이전트 계약

**역할**: indexer(스캔·파싱·검색) + dispatcher(전문가 위임).

**Pre-flight**:
1. `.claude/knowledge-librarian.json` 존재 확인 — 없으면 `/knowledge-settings` 안내
2. 각 소스 `backend` 확정(소스별 > 전역)
3. 소스 접근성: filesystem/git은 `test -d {basePath}`, obsidian은 vault search 응답 확인
4. `roots[]` 존재 확인 — 없는 root는 경고 후 스킵(전체 실패 아님)

**scope 인자**: 호출 skill은 `--source` 유무를 전달한다. 미지정 시 전체 소스 통합.

**출력 라벨**: 진행/오류 메시지에 `[librarian]` 접두를 사용한다 (`local-memory`의 `[specs]`/`[scripts]` 관례와 정합, 어휘 충돌 없음).

### 스킬 사양

#### `knowledge-index` (`/knowledge-index [--source name] [--force]`)

1. `librarian` pre-flight 수행
2. 대상 소스별로 SCAN → include/exclude 필터 → 각 파일 READ(또는 헤더만) 파싱
3. `--force`가 아니면 기존 인덱스의 `mtime`/`size`와 비교해 증분 갱신
4. `indexPath`에 인덱스 JSON 기록 (**소스에는 미기록**)
5. 보고: 소스별 문서 수, 신규/변경/삭제 건수, `generatedAt`

#### `knowledge-search` (`/knowledge-search "질의" [--source name] [--limit N]`)

1. 인덱스 로드 — 없으면 `/knowledge-index` 안내 후 중단
2. staleness 판정 → stale이면 경고 병기(결과는 반환)
3. 질의 토큰화 → `title`(×3) · `headings`(×2) · `tags`/`categories`/`series`(×2) · `summary`(×1) 가중 매칭으로 스코어링
4. `--source`/`--limit`(기본 5) 적용
5. 결과 반환: `순위 · [source] path · title · 매칭 heading · 발췌`

#### `knowledge-ask` (`/knowledge-ask "질문" [--to agent] [--source name]`)

1. `knowledge-search` 로직으로 상위 문서 선별 (기본 상위 3~5)
2. 선별 문서를 소스에서 READ하여 관련 섹션 발췌 (출처 `source`/`path` 라벨 부착)
3. `--to` 대상 에이전트 결정:
   - 지정 시: 실재 에이전트인지 확인 (`data-engineer` / `ontology-expert` / `general-purpose` 등)
   - 미지정 시: `AskUserQuestion`으로 후보 제시 (무음 기본값 금지)
4. Agent 도구로 대상 서브에이전트 호출 — 프롬프트에 질문 + 발췌 근거(출처 포함) 전달
5. 대상 에이전트의 응답을 사용자에게 반환하고, librarian은 사용한 출처 목록을 함께 보고

### 디스패치 계약 — `dispatch-contract.md`

- 전달 페이로드: `{ question, evidence: [{ source, path, title, excerpt }], instructions }`
- 대상 에이전트에게 "아래 근거만을 우선 활용하고, 부족하면 추가 탐색을 요청하라"는 지침을 명시
- 각 근거에 출처를 부착하여 대상 에이전트가 인용 가능하게 함
- 대상 에이전트는 마켓플레이스 실재 에이전트로 제한 — 존재하지 않으면 오류

## Design Decisions

1. **인덱스를 소스가 아닌 현재 repo에 둔다** — 소스 read-only 불변식(FR-5)을 구조적으로 보장. 여러 repo가 같은 wiki를 참조해도 각 repo가 자기 인덱스를 가진다.
2. **git 소스도 read-only** — `local-memory`의 git 백엔드는 commit/push하지만, knowledge-librarian의 git 소스는 워킹트리를 읽기만 한다. 두 플러그인의 git 취급이 정반대임을 문서에 명시한다.
3. **키워드 랭킹 우선** — 임베딩 없이 title/heading/tag 가중 매칭으로 시작. 시맨틱 검색은 향후 확장.
4. **dispatch를 1급 기능으로** — 단순 검색을 넘어 "indexer가 전문가에게 근거를 넘기는" 흐름을 `knowledge-ask`로 명시화. 마켓플레이스의 `data-engineer`/`ontology-expert`와 즉시 연동.

## Open Questions

| # | 질문 | 후보 |
|---|------|------|
| 1 | 인덱스 파일을 `.gitignore`에 추가할 것인가(현재 repo 오염 방지) | 기본 추가 권장 vs 사용자 선택 |
| 2 | obsidian 소스의 `mtime` 정밀도 부족 시 staleness 처리 | search 메타 근사 vs 항상 재인덱싱 권고 |
| 3 | `roots` 미지정(소스 전체) 시 대형 wiki 성능 | 최초 인덱싱 시 문서 수 경고 임계값 도입 여부 |
| 4 | `knowledge-ask`의 발췌 상한(토큰 예산) | 상위 N개 × 섹션 길이 제한 규칙 |

> 위 Open Questions는 plans.md에서 결정한다.
