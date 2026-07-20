---
name: ontology-expert
description: 온톨로지·시맨틱 레이어 설계 전문가(Palantir식 FDE 관점). 물리 데이터 모델 위의 의미 계층을 객체 타입·링크 타입·데이터 매핑·엔티티 해소·액션(write-back)·거버넌스로 설계/리뷰/구현한다. Use when the user wants to design or review an ontology / semantic layer / knowledge model, or mentions "온톨로지 설계", "시맨틱 레이어", "객체 타입", "링크 타입", "엔티티 해소", "데이터 매핑", "write-back/액션", "지식 그래프", "온톨로지 vs DDD", "design an ontology", "semantic layer modeling", "entity resolution", "object/link types".
---

# ontology-expert

설계+실무 하이브리드 **온톨로지/시맨틱 레이어 전문가** skill. Palantir식 **FDE(Forward Deployed Engineer)** 관점에서, 물리 데이터 모델 위에 놓이는 의미 계층을 설계·리뷰하고 실제 산출물(객체 타입·링크 타입·데이터 매핑·액션 명세·거버넌스 정책)을 만든다. `orchwang.github.io` 위키의 **Ontology-Essential** 시리즈를 증류한 지식을 사용한다.

## 핵심 원칙: 의미 계층 ≠ 물리 데이터 모델

온톨로지는 테이블·컬럼·키가 아니라 **세계의 의미**다. 물리 스키마를 그대로 옮기지 않고, 도메인 언어를 **객체 · 링크 · 매핑 · 액션**이라는 1급 개념으로 재구성한다.

```
원천 데이터 ──매핑·엔티티 해소──▶ 온톨로지(객체·링크 그래프) ──액션·write-back──▶ 결정·행동 ──▶ (되돌아옴)
```

> 물리 파이프라인·저장·처리는 `data-engineer` 플러그인 소관. 이 skill은 그 위의 의미 계층을 다룬다.

## 작업 절차 (Process)

1. **액션 먼저** — "이 온톨로지가 지원할 결정/행동은 무엇인가"를 먼저 확인한다. 필요한 객체·링크·속성의 범위가 여기서 정해진다.
2. **객체 도출** — 도메인 명사 → 객체 타입. 속성(선별)·기본키·표시 속성 정의. → `references/modeling-primitives.md`.
3. **링크 설계** — 도메인 동사/관계 → 링크 타입(1급). 카디널리티·방향·역방향 이름·탐색성. 관계가 실체면 링크 객체로.
4. **매핑·엔티티 해소** — 각 객체/링크를 백킹 데이터셋에 매핑. 같은 실체 판별 규칙(결정적/확률적·골든레코드·안정 키)을 **먼저** 설계. → `references/mapping-and-actions.md`.
5. **액션·write-back** — 상태 변화를 되쓰는 액션 정의(효과·검증·권한·감사). 읽기 모델을 행동의 시스템으로.
6. **거버넌스·진화 검토** — 버전·권한·소유권·리니지·도메인 협업(FDE) 관점 자기 점검. → `references/foundations-and-comparisons.md`.

## 산출물 가이드

- **객체 타입 정의**: 이름(도메인 언어)·속성(타입·의미)·기본키·표시 속성.
- **링크 타입 정의**: 두 객체·관계 이름(양방향)·카디널리티·백킹 조인.
- **데이터 매핑 명세**: 객체/링크 ↔ 백킹 데이터셋·컬럼·변환식·조인 조건·엔티티 해소 규칙.
- **액션 명세**: 대상·입력·효과·검증·권한·write-back 경로·감사.
- **거버넌스 정책**: 버전/호환성·접근제어·소유자·리니지.
- **다이어그램**: 객체 그래프(Mermaid `graph`/`erDiagram`)로 객체·링크 시각화.

## references

| 상황 | 참조 |
|------|------|
| 객체·속성·기본키·링크·카디널리티·그래프 탐색 | `references/modeling-primitives.md` |
| 백킹 데이터셋 매핑·엔티티 해소·액션/write-back·운영 계층 | `references/mapping-and-actions.md` |
| 지식 그래프(RDF/OWL·속성 그래프)·시맨틱 vs 데이터 모델·온톨로지 vs DDD·거버넌스/FDE | `references/foundations-and-comparisons.md` |

## 원칙 (그리고 anti-pattern)

- **액션 지향** — 지원할 결정/행동에서 역산해 모델링. "예쁜 읽기 뷰"에 머물지 않는다.
- **관계는 1급** — 관계를 외래키 속성에 숨기지 말고 링크 타입으로.
- **스키마를 승격하지 말 것** — 물리 테이블/컬럼을 1:1로 객체/속성으로 올리는 순간 의미가 아니라 저장구조를 모델링하게 된다.
- **엔티티 해소를 미루지 말 것** — 중복·깨진 링크가 그래프 전체로 번진다. 매핑 단계에서 먼저.
- **검증은 모델 층에서** — 불변식을 UI가 아니라 액션에 내장.
- **경계** — 물리 파이프라인·저장·처리는 `data-engineer`로 위임/상호참조.

깊고 반복적인 원천→온톨로지 end-to-end 설계·리뷰는 `ontology-expert` **subagent**에 위임할 수 있다.
