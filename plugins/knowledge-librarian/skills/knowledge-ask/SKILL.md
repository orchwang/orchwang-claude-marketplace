---
name: knowledge-ask
description: 지식 카탈로그에서 질문 관련 문서를 찾아 발췌를 모으고, 다른 전문 서브에이전트(data-engineer / ontology-expert 등)에게 근거로 전달(dispatch)하여 답을 받는다. Use when the user wants to answer a question grounded in the knowledge base or hand knowledge to a specialist, or mentions "지식 기반으로 물어봐", "wiki 근거로 ...에게 물어봐", "knowledge ask", "전문가에게 지식 전달".
---

# knowledge-ask

지식 카탈로그를 검색해 관련 발췌를 모으고, 전문 서브에이전트에게 근거로 전달하는 skill. 본 플러그인의 핵심 기능(indexer → specialist)이다.

> 검색 랭킹은 `references/index-format.md`, 위임 계약은 `references/dispatch-contract.md`를 참조한다.

## Input

- `/knowledge-ask "레이크하우스 파티셔닝 전략은?" --to data-engineer`
- `/knowledge-ask "온톨로지 링크 모델링 방법" --to ontology-expert --source eng-wiki`
- `/knowledge-ask "이 주제 정리해줘"` — `--to` 미지정 시 대상 에이전트를 대화형으로 물음

## Process

### Step 1: 컨텍스트 확인

`librarian` 에이전트를 호출하여 Pre-flight 및 `indexPath`를 수신한다. 인덱스가 없으면 `/knowledge-index`를 안내 후 중단한다.

### Step 2: 관련 문서 선별

`knowledge-search` 랭킹 로직으로 상위 문서를 선별한다 (기본 3~5개). `--source` 지정 시 한정한다.

### Step 3: 발췌 수집

선별 문서를 소스에서 READ하여 질문 관련 섹션을 발췌한다.

- 상위 문서 최대 5개, 문서당 최대 ~1500자 (`references/dispatch-contract.md` 상한)
- 각 발췌에 출처 라벨 `[{source}] {path}`를 부착한다

### Step 4: 대상 에이전트 결정

- `--to` 지정 시: 실재 에이전트인지 확인한다 (`data-engineer` / `ontology-expert` / `general-purpose` 등). 미존재 시 "에이전트 '{name}'을 찾을 수 없습니다. 사용 가능한 에이전트: ..." 안내 후 중단
- `--to` 미지정 시: `AskUserQuestion`으로 질문 성격에 맞는 후보를 제시한다. **무음 기본값을 적용하지 않는다.**

### Step 5: 디스패치

Agent 도구로 대상 서브에이전트를 호출한다. 프롬프트에 아래를 마크다운으로 직렬화하여 전달한다:

- `question`: 사용자 질문
- `evidence[]`: `{ source, path, title, excerpt }` 목록 (출처 라벨 포함)
- `instructions`: "아래 evidence를 우선 근거로 답하라. 부족하면 추가 탐색을 요청하라. 인용 시 [source] path를 명시하라."

### Step 6: 결과 보고

`[librarian]` 라벨 접두. 대상 에이전트 응답과 함께 사용한 출처 목록을 보고한다.

```
[librarian] data-engineer 응답 (근거: 3개 문서)

{대상 에이전트 응답}

사용한 출처:
  - [blog] _posts/Technology/Data-Engineering/2025-08-01-lakehouse.md
  - [blog] _posts/Technology/Data-Engineering/2025-08-15-partitioning.md
```
