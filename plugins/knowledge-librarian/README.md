# knowledge-librarian

사람이 별도로 관리하는 wiki/지식 저장소(md 문서 모음)를 **read-only** 지식 소스로 지정하여, 카탈로그화·검색(indexer)하고 관련 지식을 다른 전문 서브에이전트에게 근거로 전달(dispatch)하는 Claude Code 플러그인입니다.

## 개요

`knowledge-librarian`은 지정한 wiki repo(또는 로컬 디렉토리)의 특정 위치에 있는 md 문서를 Claude Code 작업의 **근거 지식**으로 읽어 들입니다. `librarian` 에이전트가 문서를 경량 카탈로그로 인덱싱하고, 자연어로 검색하며, 관련 발췌를 `data-engineer`·`ontology-expert` 같은 전문 서브에이전트에게 출처와 함께 넘겨 답을 받습니다.

### local-memory와의 차이 (write-out vs read-in)

| 축 | local-memory | knowledge-librarian |
|---|---|---|
| 데이터 방향 | 작업 산출물을 밖으로 **write** | 큐레이션된 지식을 안으로 **read** |
| 소스 소유권 | Claude/repo가 생성 | 사람이 별도 관리하는 wiki (read-only) |
| 스코프 | `{repo-name}/` 단위 | 도메인/토픽 단위, 여러 repo가 공유 |
| 핵심 역할 | 기록(capture) | 탐색(index) + 전문가 전달(dispatch) |
| git 취급 | 커밋/푸시(write) | 워킹트리 읽기만(read-only) |
| 설정 파일 | `.claude/local-memory.json` | `.claude/knowledge-librarian.json` |

> 두 플러그인은 설정·명령이 분리되어 동시에 사용할 수 있습니다.

## 요구 사항

- **Git** — filesystem/git 소스는 로컬 경로, git 소스는 워킹트리를 읽습니다 (커밋 없음)
- **Obsidian 앱** — obsidian 소스를 사용할 때만 (kepano/obsidian-skills 플러그인)

## 설치

```bash
/plugin install knowledge-librarian@orchwang-marketplace
```

## 설정

`.claude/knowledge-librarian.json`에 지식 소스를 지정합니다. `/knowledge-settings`로 대화형 설정도 가능합니다.

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

### 설정 항목

| 항목 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `backend` | 선택 | 전역 기본 backend (`obsidian`/`filesystem`/`git`) | `git` |
| `indexPath` | 선택 | 카탈로그 저장 경로(현재 repo 기준) | `.claude/knowledge-index.json` |
| `sources[]` | 필수 | 지식 소스 배열 (1개 이상) | — |
| `sources[].name` | 필수 | 소스 식별자 | — |
| `sources[].backend` | 선택 | 소스별 backend (미지정 시 전역 상속) | 전역 `backend` |
| `sources[].basePath` | filesystem/git | 소스 저장소 루트 절대경로 | — |
| `sources[].vault` | obsidian | obsidian vault 이름 | — |
| `sources[].roots[]` | 선택 | 지식 대상 하위 경로 | `[]`(전체) |
| `sources[].include[]` | 선택 | 포함 글롭 | `["**/*.md"]` |
| `sources[].exclude[]` | 선택 | 제외 글롭 | `[]` |

> 소스는 **항상 read-only**입니다 — 플러그인은 소스에 어떤 파일도 쓰지 않고 git commit/push도 하지 않습니다.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/knowledge-settings` | 지식 소스 설정 검토·대화형 보완 |
| `/knowledge-index [--source name] [--force]` | 소스를 스캔하여 카탈로그 (재)구축 |
| `/knowledge-search "질의" [--source name] [--limit N]` | 카탈로그 랭킹 검색·발췌 반환 |
| `/knowledge-ask "질문" [--to agent] [--source name]` | 관련 지식을 전문 서브에이전트에게 근거로 전달 |

## 스킬

| 스킬 | 설명 |
|------|------|
| `knowledge-index` | 카탈로그 (재)구축 (증분/`--force` 전체) |
| `knowledge-search` | 자연어 랭킹 검색 (title×3/heading×2/tag·category·series×2/summary×1) |
| `knowledge-ask` | 검색 + 전문가 서브에이전트 디스패치 (indexer → specialist) |

## 에이전트

| 에이전트 | 설명 |
|----------|------|
| `librarian` | indexer(스캔·파싱·검색) + dispatcher(전문가 위임). read-only 불변식 보장 |

## 인덱스 구조

인덱스는 **소스가 아니라 현재 repo**의 `indexPath`에 저장됩니다.

```
{현재 repo}/
  .claude/
    knowledge-librarian.json   # 설정
    knowledge-index.json       # 카탈로그 (generatedAt · sources · entries[])
```

각 엔트리: `source` · `path` · `title` · `headings[]` · `tags[]` · `categories[]` · `series` · `summary` · `size` · `mtime`.

## 사용 예 (Jekyll 블로그)

```bash
/knowledge-settings                                  # 소스 설정
/knowledge-index                                     # _posts/ 212개 인덱싱
/knowledge-search "온톨로지 링크 모델링"               # 관련 글 검색
/knowledge-ask "레이크하우스 파티셔닝 전략" --to data-engineer   # 근거 첨부 위임
```

- `roots: ["_posts/"]`이 Jekyll 생성물 `_site/`의 md 중복을 배제
- Jekyll frontmatter(`title`/`tags`/`categories`/`excerpt`/`series`/`published`) 자동 파싱, `published: false` 초안 제외

## 라이선스

MIT
