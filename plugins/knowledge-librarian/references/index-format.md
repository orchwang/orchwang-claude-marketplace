# Index Format Reference

`knowledge-librarian`의 지식 카탈로그(인덱스) 스키마와 파싱·staleness·증분 갱신 규칙.

> 인덱스는 소스 저장소가 **아니라** 현재 repo의 `indexPath`(기본 `.claude/knowledge-index.json`)에 저장한다. 소스 read-only 불변식을 구조적으로 보장한다.

## 카탈로그 JSON 스키마

```json
{
  "generatedAt": "2026-07-21T10:00:00+09:00",
  "sources": {
    "blog": { "docCount": 212, "roots": ["_posts/"] }
  },
  "entries": [
    {
      "source": "blog",
      "path": "_posts/Technology/Ontology/2025-09-01-ontology-basics.md",
      "title": "온톨로지 기초",
      "headings": ["배경", "객체와 링크", "엔티티 해소"],
      "tags": ["ontology", "semantic-layer"],
      "categories": ["Technology", "Ontology"],
      "series": "ontology-101",
      "summary": "온톨로지 설계의 기본 개념을 객체·링크 중심으로 정리한다.",
      "size": 8241,
      "mtime": "2025-09-01T14:22:00+09:00"
    }
  ]
}
```

## 엔트리 필드

| 필드 | 설명 |
|------|------|
| `source` | 소스 `name` |
| `path` | 소스 루트 기준 상대경로 |
| `title` | 문서 제목 |
| `headings[]` | H2/H3 텍스트 목록 |
| `tags[]` | frontmatter `tags` |
| `categories[]` | frontmatter `categories` (있을 때) |
| `series` | frontmatter `series` 문자열 (있을 때) |
| `summary` | 문서 요약 |
| `size` | 바이트 크기 |
| `mtime` | 최종 수정 시각 (ISO8601) |

## 파싱 규칙

- **파싱 순서**: frontmatter → 첫 H1 → H2/H3 수집 → summary
- **title 우선순위**: frontmatter `title` > 첫 H1 > 파일명(확장자 제거)
- **summary 우선순위**: frontmatter `summary` > `description` > `excerpt`(Jekyll 관례) > 첫 비어있지 않은 문단(최대 280자)
- **facet 필드**: `tags` → `tags[]`, `categories` → `categories[]`, `series` → `series`(문자열, 있을 때만)
- **published 필터**: frontmatter `published: false`(Jekyll 초안)인 문서는 인덱스에서 **제외**한다 (기본 동작)

## Staleness 판정 (FR-8)

- 임의의 소스 파일 `mtime` > 인덱스 `generatedAt` → **stale**
- 검색·디스패치 시 stale이면 결과는 반환하되 "인덱스가 오래되었을 수 있음 — `/knowledge-index` 권장" 경고를 병기한다
- obsidian 소스는 `mtime` 근사가 어려우므로 "obsidian 소스는 수동 재인덱싱 권장" 경고를 상시 병기한다 (강제 차단 없음)
- 인덱스 자체가 없으면 검색을 중단하고 `/knowledge-index`를 먼저 안내한다

## 증분 갱신

- 기존 엔트리의 `size` / `mtime`과 현재 파일을 비교한다
- **변경 / 신규**만 재파싱한다
- 소스에서 사라진 파일의 엔트리는 제거한다
- `--force`이면 기존 인덱스를 무시하고 전체 재구축한다

## 대형 소스 경고 (Open Q3 결정)

- 최초 인덱싱에서 대상 문서 수가 임계값(기본 **500**) 초과 시 경고하고 `roots` / `exclude` 축소를 권고한다
- 중단하지는 않는다 (경고 후 진행)
