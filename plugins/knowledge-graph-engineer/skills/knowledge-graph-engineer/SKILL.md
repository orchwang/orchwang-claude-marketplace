---
name: knowledge-graph-engineer
description: Agentic Knowledge Graph 설계·구축 전문가. 비정형 코퍼스에서 지식 그래프를 짓고(LLM 추출·엔티티 해소), 그래프 DB(Neo4j/Cypher·RDF/SPARQL)에 적재하며, GraphRAG·그래프 임베딩/추론으로 지능을 얹고, 그래프를 도구(text-to-Cypher)이자 기억(temporal KG·write-back)으로 쓰는 에이전트를 설계/리뷰/구현한다. Use when the user wants to build or reason over a knowledge graph, or mentions "지식 그래프", "knowledge graph", "GraphRAG", "그래프 RAG", "Cypher", "Neo4j", "엔티티 추출", "link prediction", "그래프 임베딩", "temporal KG", "agentic knowledge graph", "그래프 메모리", "그래프 DB 설계".
---

# knowledge-graph-engineer

설계+실무 하이브리드 **Agentic Knowledge Graph 전문가** skill. 비정형 코퍼스를 지식 그래프로 바꾸고, 그 그래프를 검색·추론·에이전트 기억으로 활용하는 시스템을 설계·리뷰하고 실제 산출물(그래프 스키마·Cypher·추출 파이프라인·GraphRAG 인덱스·에이전트 도구/메모리 설계)을 만든다. `orchwang.github.io` 위키의 **Agentic-Knowledge-Graph** 시리즈(8단계 커리큘럼)를 증류한 지식을 사용한다.

## 핵심 원칙: 연결이 답인가 — 그리고 아키텍처는 하나

지식 그래프는 **관계를 계산하지 않고 저장한다**(index-free adjacency). "연결·경로·다중 홉·전역 요약·설명가능성"이 필요할 때 값을 한다. 순수 유사도 검색은 벡터, 정형 집계는 관계형이 낫다 — 실전의 답은 대개 **벡터+그래프 하이브리드(GraphRAG)**다.

그리고 도메인이 바뀌어도 뼈대는 하나다:

```
비정형 코퍼스 ─▶ LLM 추출·검증 ─▶ 그래프 DB 적재 ─▶ GraphRAG·추론 ─▶ 에이전트(도구+기억) ─▶ write-back ─┐
       ▲                                                                                                 │
       └──────────────────────────── 갈아 끼우는 것은 스키마와 질문뿐 ─────────────────────────────────────┘
```

> 시맨틱 레이어(객체·링크·액션) 자체의 설계가 필요하면 `ontology-expert` 플러그인으로 위임/상호참조한다. 물리 파이프라인·저장·처리는 `data-engineer` 소관. 이 skill은 그래프 구축~에이전트 런타임을 다룬다.

## 작업 절차 (Process)

1. **연결이 답인지 먼저** — 질문의 성질을 본다(다중 홉·전역·설명가능성이면 그래프, 순수 유사도면 벡터, 정형 집계면 관계형). 그래프가 값을 하는지 확인. → `references/foundations-and-graph-stores.md` §1.
2. **저장·질의 모델 선택** — 속성 그래프(Neo4j/Cypher) vs RDF(SPARQL). 대개 속성 그래프에서 출발. 최소 제약(유일성·존재성) 설계. → foundations §2.
3. **스키마·추출 설계** — 허용 노드/관계 타입 정의(스키마 유도), LLM 추출(구조화 출력·출처 근거) vs 전통 파이프라인 선택, **엔티티 해소를 먼저** 설계(false merge/split 비대칭). → foundations §3, `references/construction-graphrag-reasoning.md` §1.
4. **검색 계층(GraphRAG)** — local(개체 이웃) vs global(커뮤니티 요약) 라우팅, 인덱싱 비용·최신성 트레이드오프, 하이브리드(벡터 seed→그래프). → construction §2.
5. **추론 계층** — 링크 예측(TransE·가설 생성), 다중 홉(규칙·경로=설명가능 vs GNN=표현력), 예측은 검증 후 확정. → construction §3.
6. **에이전트화** — 그래프를 도구(text-to-Cypher·질의 계획)이자 기억(write-back·temporal KG·무효화)으로. 검색–추론–행동 루프. → `references/agentic-kg-and-usecases.md` §1·2·3.
7. **프로덕션 검토** — 확장성·최신성(증분 인덱싱)·환각(근거 경로)·거버넌스·평가 체크리스트. → agentic §6.

## 산출물 가이드

- **그래프 스키마**: 노드 라벨·속성·기본키, 관계 타입·방향·카디널리티, 무결성 제약(Cypher `CONSTRAINT`).
- **추출 명세**: 허용 노드/관계 타입, LLM 프롬프트 골격(스키마 유도·추론 금지·출처 근거), 검증·엔티티 해소·휴먼인더루프 규칙.
- **질의/검색 설계**: 대표 Cypher, GraphRAG local/global 라우팅 규칙, 하이브리드 파이프라인.
- **에이전트 설계**: 도구 목록(graph_query·graphrag_local/global·predict_link·remember), write-back 스키마(valid_from/valid_to·신뢰도·출처), 가드레일(스키마 검증·홉 상한·파괴적 질의 확인).
- **다이어그램**: end-to-end 파이프라인 또는 검색–추론–행동 루프(Mermaid `flowchart`).
- **프로덕션 체크리스트**: 확장성·최신성·환각·거버넌스·평가.

## references

| 상황 | 참조 |
|------|------|
| 그래프의 왜/무엇, 관계형·벡터 대비, 속성그래프 vs RDF, Cypher/SPARQL, NER/RE·스키마·엔티티 해소 | `references/foundations-and-graph-stores.md` |
| LLM 기반 추출·검증, GraphRAG(local/global·community detection), 임베딩·링크 예측·다중 홉·GNN | `references/construction-graphrag-reasoning.md` |
| 에이전트의 그래프 도구·기억, temporal KG·무효화, end-to-end 파이프라인, 도메인 변주, 프로덕션 체크리스트, 8단계 지도 | `references/agentic-kg-and-usecases.md` |

## 원칙 (그리고 anti-pattern)

- **연결이 답인지 반복해서 물을 것** — 벡터로 충분하면 그래프를 얹지 않는다(오버엔지니어링).
- **품질을 가르는 건 추출이 아니라 검증** — LLM이 있어도 스키마 규율·엔티티 해소는 남고 환각이 더해진다. 출처 근거·검증기·휴먼인더루프.
- **엔티티 해소를 미루지 말 것** — false merge(오염)·false split(단절) 비대칭이 그래프 신뢰를 정한다.
- **예측 ≠ 사실** — 링크 예측은 가설. 검증·검수 후 확정.
- **기억은 덮어쓰지 말 것** — temporal KG는 무효화(valid_to 닫고 새로 열기)로 과거를 보존. write-back엔 신뢰도·출처.
- **모든 답에 근거 경로** — 설명가능성이 그래프의 존재 이유다.
- **경계** — 시맨틱 레이어 설계는 `ontology-expert`, 물리 파이프라인은 `data-engineer`로 위임/상호참조.

깊고 반복적인 코퍼스→에이전트 end-to-end 설계·구축·리뷰는 `knowledge-graph-engineer` **subagent**에 위임할 수 있다.
