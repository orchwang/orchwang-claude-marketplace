# knowledge-graph-engineer

Agentic Knowledge Graph **설계+실무 하이브리드 전문가** 플러그인입니다. 비정형 코퍼스를 지식 그래프로 바꾸고(LLM 추출·엔티티 해소), 그래프 DB(Neo4j/Cypher·RDF/SPARQL)에 적재하며, GraphRAG·그래프 임베딩/추론으로 지능을 얹고, 그래프를 **도구(text-to-Cypher)이자 기억(temporal KG·write-back)**으로 쓰는 에이전트까지 설계·리뷰·구현합니다.

## 개요

`orchwang.github.io` 위키의 **Agentic-Knowledge-Graph** 시리즈(8단계 커리큘럼)를 증류했습니다. "연결이 답인가"를 판단 기준으로, 코퍼스→추출→그래프→GraphRAG·추론→에이전트 write-back으로 이어지는 하나의 뼈대를 도메인마다 변주합니다.

### 핵심 원칙

- **연결이 답인가** — 다중 홉·전역·설명가능성이면 그래프, 순수 유사도면 벡터, 정형 집계면 관계형. 실전의 답은 대개 벡터+그래프 하이브리드(GraphRAG).
- **아키텍처는 하나, 변주는 도메인마다** — 갈아 끼우는 것은 스키마(허용 노드/관계)와 질문뿐.
- **품질을 가르는 건 추출이 아니라 검증** — 엔티티 해소·출처 근거·휴먼인더루프.
- **기억은 무효화로 축적** — temporal KG는 사실을 덮어쓰지 않고 valid_to로 닫고 새로 연다.

## 구성

- **`knowledge-graph-engineer` skill** — 그래프 구축~에이전트 런타임 설계/리뷰/구현, 산출물 가이드
- **`knowledge-graph-engineer` agent** — 코퍼스→에이전트 end-to-end 8단계 자율 설계·구축
- **references 3종**(progressive disclosure):
  - `foundations-and-graph-stores.md` — 왜 그래프인가, 속성그래프 vs RDF, Cypher/SPARQL, NER/RE·스키마·엔티티 해소
  - `construction-graphrag-reasoning.md` — LLM 추출·검증, GraphRAG(local/global), 임베딩·링크 예측·다중 홉·GNN
  - `agentic-kg-and-usecases.md` — 에이전트 도구·기억, temporal KG·무효화, end-to-end 파이프라인, 도메인 변주, 프로덕션 체크리스트

## 설치

```bash
/plugin install knowledge-graph-engineer@orchwang-marketplace
```

## 사용 예

```
지식 그래프 만들어줘: 사내 인시던트 리포트 코퍼스로 GraphRAG Q&A를 하고 싶어
GraphRAG local vs global 라우팅을 어떻게 설계하지?
에이전트가 대화에서 배운 사실을 그래프 메모리로 쌓게 하고 싶어 (temporal KG)
이 도메인에서 링크 예측으로 추천을 만들 수 있을까?
```

## 인접 전문가와의 경계

| 관심사 | 담당 |
|--------|------|
| 그래프 구축·검색·추론·에이전트 런타임 | **knowledge-graph-engineer** (본 플러그인) |
| 시맨틱 레이어 설계(객체·링크·액션·거버넌스) | `ontology-expert` |
| 물리 파이프라인·저장·처리·수집 | `data-engineer` |
| wiki/지식 저장소를 read-only로 인덱싱·검색·전달 | `knowledge-librarian` |

- 그래프 구축 3단계(스키마·온톨로지 설계)에서 시맨틱 레이어 설계가 필요하면 `ontology-expert`로 위임합니다.
- `knowledge-librarian`이 KG 관련 질문을 본 전문가에게 근거와 함께 dispatch하는 구성과도 자연스럽게 맞물립니다.

## 라이선스

MIT
