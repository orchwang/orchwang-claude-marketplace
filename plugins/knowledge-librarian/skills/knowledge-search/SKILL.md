---
name: knowledge-search
description: 지식 카탈로그를 자연어 질의로 랭킹 검색하여 관련 문서와 발췌를 반환한다. Use when the user wants to search the knowledge base, or mentions "지식 검색", "wiki 검색", "knowledge search", "문서 찾아줘", "관련 문서 찾아".
---

# knowledge-search

지식 카탈로그를 검색하여 관련 문서와 발췌를 반환하는 skill.

> 카탈로그 스키마·staleness는 `references/index-format.md`, 백엔드 read 매핑은 `references/source-config.md`를 참조한다.

## Input

- `/knowledge-search "온톨로지 설계 원칙"` — 전체 소스 검색
- `/knowledge-search "iceberg 테이블 규약" --source eng-wiki` — 특정 소스 한정
- `/knowledge-search "python 테스트" --limit 10` — 반환 개수 지정 (기본 5)

## Process

### Step 1: 컨텍스트 확인

`librarian` 에이전트를 호출하여 Pre-flight 및 `indexPath`를 수신한다.

### Step 2: 인덱스 로드

`indexPath`에서 카탈로그를 읽는다.

- 인덱스가 없으면: "[librarian] 인덱스가 없습니다. 먼저 `/knowledge-index`를 실행하세요." 안내 후 **중단**
- staleness 판정: 임의의 소스 파일 `mtime` > `generatedAt` → stale
  - stale이면 결과는 반환하되 "[librarian] 경고: 인덱스가 오래되었을 수 있습니다 — `/knowledge-index` 권장"을 병기
  - obsidian 소스는 "수동 재인덱싱 권장" 경고를 상시 병기

### Step 3: 랭킹

질의를 토큰화하여 각 엔트리에 대해 가중 매칭 스코어를 계산한다.

| 필드 | 가중치 |
|------|--------|
| `title` | ×3 |
| `headings` | ×2 |
| `tags` / `categories` / `series` | ×2 |
| `summary` | ×1 |

- `--source` 지정 시 해당 소스로 한정한다
- `--limit N`(기본 5)으로 상위 N개를 취한다

### Step 4: 발췌

상위 결과 각각에 대해 매칭 근거를 요약한다. 필요 시 소스에서 READ하여 관련 heading 섹션을 짧게 발췌한다 (`cat` / obsidian `read`).

### Step 5: 결과 보고

`[librarian]` 라벨 접두. 각 결과에 출처를 명시한다.

```
[librarian] "온톨로지 설계 원칙" 검색 결과 (상위 3):

1. [blog] _posts/Technology/Ontology/2025-09-01-ontology-basics.md
   온톨로지 기초 · heading: 객체와 링크, 엔티티 해소
   발췌: 온톨로지 설계는 객체·링크를 1급으로 다루며 ...

2. ...
```
