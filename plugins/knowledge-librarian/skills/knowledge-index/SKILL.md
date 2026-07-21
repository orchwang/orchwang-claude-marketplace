---
name: knowledge-index
description: 지정된 wiki/지식 소스(md)를 스캔·파싱하여 경량 카탈로그(인덱스)를 (재)구축한다. 인덱스는 현재 repo의 indexPath에만 저장하며 소스는 변경하지 않는다. Use when the user wants to (re)build the knowledge catalog, or mentions "지식 인덱싱", "wiki 인덱스", "knowledge index", "카탈로그 갱신", "인덱스 재구축".
---

# knowledge-index

지식 소스를 스캔하여 카탈로그를 (재)구축하는 skill.

> 백엔드 read 매핑은 `references/source-config.md`, 카탈로그 스키마·파싱·staleness는 `references/index-format.md`를 참조한다.

## Input

- `/knowledge-index` — 전체 소스 인덱싱
- `/knowledge-index --source blog` — 특정 소스만 인덱싱
- `/knowledge-index --force` — 증분 무시, 전체 재구축

## Process

### Step 1: 컨텍스트 확인

`librarian` 에이전트를 호출하여 Pre-flight check 및 컨텍스트를 수신한다.

수신 인자:
- `sources[]`: 각 소스의 `name` / `backend` / `basePath`|`vault` / `roots` / `include` / `exclude`
- `indexPath`: 인덱스 저장 경로 (기본 `.claude/knowledge-index.json`)

`--source` 지정 시 해당 소스만 대상으로 한다.

### Step 2: 문서 스캔

각 대상 소스·root에 대해 SCAN한다.

```bash
# filesystem / git
find "{basePath}/{root}" -name "*.md" -type f
```

- `include` / `exclude` 글롭으로 결과를 후처리 필터링한다
- obsidian은 `obsidian vault="{vault}" search query="path:{root}"`로 목록을 얻는다
- 대상 문서 수가 500 초과 시 경고하고 `roots`/`exclude` 축소를 권고한다 (중단하지 않음)

### Step 3: 파싱

각 문서에 대해:

1. `--force`가 아니면 기존 인덱스 엔트리의 `size`/`mtime`과 현재 파일을 비교한다 → 변경/신규만 재파싱
2. 파일을 READ하여 frontmatter + 헤딩 + 요약을 파싱한다 (`references/index-format.md` 규칙)
   - `title`: frontmatter `title` > 첫 H1 > 파일명
   - `headings[]`: H2/H3
   - `tags[]` / `categories[]` / `series`: frontmatter
   - `summary`: frontmatter `summary` > `description` > `excerpt` > 첫 문단(≤280자)
3. frontmatter `published: false`인 문서는 제외한다
4. `size` / `mtime`을 기록한다 (`stat`)

소스에서 사라진 파일의 엔트리는 제거한다.

### Step 4: 인덱스 기록

`indexPath`(현재 repo 기준)에 카탈로그 JSON을 쓴다.

> **소스 저장소에는 어떤 파일도 쓰지 않는다.** git 소스에 commit/push 하지 않는다.

- `generatedAt`을 현재 시각으로 갱신한다
- `sources` 요약(소스별 `docCount`, `roots`)을 갱신한다

### Step 5: 결과 보고

모든 출력에 `[librarian]` 라벨을 접두로 사용한다.

```
[librarian] 인덱스 갱신 완료: {indexPath}

소스별 문서 수:
  - blog: 212개 (신규 3, 변경 5, 삭제 1)

총 {N}개 문서, generatedAt {ISO8601}
```
