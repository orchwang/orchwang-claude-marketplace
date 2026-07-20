# ontology-expert

온톨로지·시맨틱 레이어 **설계+실무 하이브리드 전문가** 플러그인입니다. Palantir식 **FDE(Forward Deployed Engineer)** 관점으로, 물리 데이터 모델 위에 놓이는 의미 계층을 설계·리뷰·구현하고 실제 산출물(객체 타입·링크 타입·데이터 매핑·액션 명세·거버넌스 정책)을 만들어 줍니다.

`orchwang.github.io` 위키의 **Ontology-Essential** 시리즈(의미 계층의 정의 → 형식 기반·지식 그래프 → 객체 타입·속성 → 링크 타입·관계 → 소스 매핑·엔티티 해소 → 액션·운영(write-back) → 거버넌스·FDE 워크플로, 그리고 온톨로지 vs DDD 심화)를 증류해 재사용 가능한 전문가 자산으로 패키징했습니다.

## 개요

- **핵심 원칙**: 온톨로지는 물리 데이터 모델이 아니라 그 **위의 의미 계층**입니다. 도메인 언어를 객체·링크·매핑·액션이라는 1급 개념으로 재구성합니다.
- **액션 지향**: "이 온톨로지가 지원할 결정/행동"에서 역산해 모델 범위를 정합니다. 읽기 모델을 write-back으로 **행동의 시스템**으로 만듭니다.
- **progressive disclosure**: 얇은 SKILL 본문 + 깊은 `references/` 3종.

## 설치

```bash
# 마켓플레이스 추가 (최초 1회)
/plugin marketplace add orchwang/orchwang-claude-marketplace

# 플러그인 설치
/plugin install ontology-expert@orchwang-marketplace
```

## 스킬 (Skills)

| 스킬 | 설명 |
|------|------|
| `ontology-expert` | 의미 계층/온톨로지 설계에 인라인으로 반응. "의미 계층 ≠ 물리 데이터 모델"을 판단 프레임으로, 객체·링크·매핑·액션 산출물 가이드와 references로 실무를 지원. |

**references (progressive disclosure)**

- `references/modeling-primitives.md` — 객체 타입·속성·기본키·링크 타입·카디널리티·그래프 탐색
- `references/mapping-and-actions.md` — 백킹 데이터셋·엔티티 해소·액션/write-back·운영 계층
- `references/foundations-and-comparisons.md` — 지식 그래프(RDF/OWL·속성 그래프)·시맨틱 vs 데이터 모델·온톨로지 vs DDD·거버넌스/FDE

## 에이전트 (Agents)

| 에이전트 | 설명 |
|----------|------|
| `ontology-expert` | 도메인 이해(액션에서 출발)→객체 도출→링크 설계→매핑·엔티티 해소→액션/write-back→거버넌스 검토의 6단계 FDE 워크플로로 원천 데이터를 온톨로지로 end-to-end 설계·리뷰하는 자율 에이전트. |

## 빠른 시작

설치 후 아래처럼 요청하면 스킬/에이전트가 활성화됩니다.

```
# 인라인 설계 자문
"우리 커머스 도메인(고객·주문·제품·배송)을 온톨로지 객체·링크로 모델링해줘."

# 매핑·엔티티 해소
"CRM과 결제 DB에 흩어진 고객을 하나의 고객 객체로 잇는 엔티티 해소 규칙을 설계해줘."

# 액션/write-back
"'주문 환불 승인' 액션을 정의해줘. 검증·권한·write-back 경로까지."

# 비교/자문
"온톨로지와 DDD는 뭐가 다르고 어떻게 같이 쓰지?"

# end-to-end (에이전트 위임)
"ontology-expert 에이전트로 이 원천 데이터에서 온톨로지를 처음부터 설계해줘: ..."
```

## 출처

이 플러그인의 지식은 orchwang 위키의 학습 시리즈에서 증류되었습니다.

- Ontology-Essential (의미 계층·객체·링크·매핑·엔티티 해소·액션/write-back·거버넌스·FDE 워크플로)
- 심화편: 온톨로지 vs 도메인 주도 설계(DDD)

## 라이선스

MIT
