# Specs: ontology-expert plugin

> Created: 2026-07-20
> Status: Draft

## 1. 패키지 구조

```
plugins/ontology-expert/
  plugin.json
  README.md
  skills/
    ontology-expert/
      SKILL.md
      references/
        modeling-primitives.md
        mapping-and-actions.md
        foundations-and-comparisons.md
  agents/
    ontology-expert/
      AGENT.md
```

## 2. plugin.json

```json
{
  "name": "ontology-expert",
  "version": "1.0.0",
  "description": "온톨로지·시맨틱 레이어 설계 전문가(FDE 관점) — 객체·링크·데이터 매핑·액션(write-back)·거버넌스를 설계 자문과 산출물 생성으로 지원",
  "author": { "name": "orchwang" },
  "homepage": "https://github.com/orchwang/orchwang-claude-marketplace",
  "repository": "https://github.com/orchwang/orchwang-claude-marketplace.git",
  "license": "MIT",
  "keywords": ["ontology", "semantic-layer", "data-modeling", "knowledge-graph", "entity-resolution", "fde", "write-back"]
}
```

## 3. SKILL.md 사양

### 3.1 Frontmatter

- `name: ontology-expert`
- `description`: 무엇을 하는지 + 트리거(한/영). 예: "온톨로지/의미 계층을 설계·리뷰… '온톨로지 설계', '객체 타입', '링크 타입', '엔티티 해소', '시맨틱 레이어', 'design an ontology', 'semantic layer modeling'."

### 3.2 본문 섹션

1. **역할 정의** — FDE식 설계+실무 온톨로지 전문가.
2. **핵심 원칙: 의미 계층 ≠ 물리 데이터 모델** — 온톨로지는 테이블/스키마 위에 놓인 "세계의 의미" 계층. 객체·링크·매핑·액션이 1급 개념.
3. **작업 절차(Process)** — (1) 도메인 언어를 객체·링크 후보로 (2) 속성·기본키 정의 (3) 링크와 카디널리티 (4) 백킹 데이터셋 매핑·엔티티 해소 (5) 액션/write-back으로 "읽기 모델"을 "행동의 시스템"으로 (6) 거버넌스·진화 관점 검토.
4. **산출물 가이드** — 객체 타입 정의 / 링크 타입 정의 / 데이터 매핑 명세 / 액션 명세 / 거버넌스 정책 각각의 최소 기준.
5. **references 안내**.
6. **원칙(anti-patterns 포함)** — 물리 스키마를 그대로 객체로 승격하지 말 것, 관계를 속성에 숨기지 말 것(링크를 1급으로), 엔티티 해소를 매핑 단계로 미루지 말 것.

### 3.3 references 매핑

| 상황 | 참조 |
|------|------|
| 객체·속성·기본키·링크·카디널리티·그래프 탐색 | `references/modeling-primitives.md` |
| 백킹 데이터셋 매핑·엔티티 해소·액션/write-back·운영 계층 | `references/mapping-and-actions.md` |
| 지식 그래프(RDF/OWL·속성 그래프)·시맨틱 vs 데이터 모델·온톨로지 vs DDD·거버넌스/FDE | `references/foundations-and-comparisons.md` |

## 4. AGENT.md 사양

### 4.1 Frontmatter

- `name: ontology-expert`
- `description`: 원천 데이터→온톨로지 end-to-end 설계·리뷰 자율 에이전트 + 트리거.

### 4.2 FDE 설계 워크플로

1. **도메인 이해** — 어떤 결정을 내리려 하는가(액션이 먼저), 어떤 원천 데이터가 있는가.
2. **객체 후보 도출** — 도메인 명사 → 객체 타입, 속성·기본키.
3. **링크 설계** — 도메인 동사/관계 → 링크 타입, 카디널리티·방향·탐색성.
4. **매핑·엔티티 해소** — 각 객체/링크를 백킹 데이터셋에 매핑, 동일 실체 판별 규칙.
5. **액션·write-back 설계** — 어떤 상태 변화를 온톨로지에 되쓰는가, 검증·권한.
6. **거버넌스·진화 검토** — 버전·권한·소유권·도메인 협업(FDE) 관점 자기 리뷰.

### 4.3 규칙

- 항상 "이 온톨로지가 지원할 결정/액션"을 먼저 확인한다(액션 지향).
- 물리 테이블 구조를 그대로 옮기지 않는다(의미 중심 재구성).
- 입력이 부족하면 도메인·소스·의사결정에 대해 질문한다.
- skill의 references를 지식원으로 재사용한다.

## 5. README.md 필수 섹션

개요 / 설치 / 스킬 / 에이전트 / 빠른 시작(예시 프롬프트) / 출처(위키 시리즈) / 라이선스.

## 6. 등록 변경

- `.claude-plugin/marketplace.json` plugins 배열에 `ontology-expert` 추가
- 루트 `README.md` 카탈로그 갱신
- `CHANGELOG.md` 항목 추가
- 마켓플레이스 루트 `plugin.json` version 마이너 bump(data-engineer와 함께 한 번에)
