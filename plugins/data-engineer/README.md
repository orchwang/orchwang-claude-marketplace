# data-engineer

데이터 엔지니어링 **설계+실무 하이브리드 전문가** 플러그인입니다. 데이터 파이프라인·데이터 플랫폼을 설계·리뷰·구현하고, 실제 산출물(아키텍처 설계, Airflow DAG, dbt 모델, Kafka·Spark 코드, Iceberg 테이블 설계)까지 만들어 줍니다.

`orchwang.github.io` 위키의 **Data-Engineering-Essential** 시리즈(정의·역사 → 수집·저장·처리·오케스트레이션 → 아키텍처·사례 → 품질·거버넌스·DataOps, 그리고 Airflow·dbt·Kafka·Spark·Lakehouse(Iceberg)·Stream Processing(Flink) 심화)를 증류해 재사용 가능한 전문가 자산으로 패키징했습니다.

## 개요

- **판단 프레임**: 모든 요청을 데이터 엔지니어링 수명주기(생성→수집→저장→변환→서빙)의 한 칸에 놓고, 저류(보안·데이터관리·DataOps·아키텍처·오케스트레이션·SWE)를 함께 봅니다.
- **설계 자문 + 산출물 생성**: 아키텍처 리뷰·기술 선택·트레이드오프 자문과 함께 DAG·모델·잡·테이블 설계 같은 실물을 만듭니다.
- **progressive disclosure**: 얇은 SKILL 본문 + 깊은 `references/` 3종.

## 설치

```bash
# 마켓플레이스 추가 (최초 1회)
/plugin marketplace add orchwang/orchwang-claude-marketplace

# 플러그인 설치
/plugin install data-engineer@orchwang-marketplace
```

## 스킬 (Skills)

| 스킬 | 설명 |
|------|------|
| `data-engineer` | 파이프라인·플랫폼 설계/리뷰/구현에 인라인으로 반응. 수명주기+저류를 판단 프레임으로, 산출물 가이드와 references로 실무를 지원. |

**references (progressive disclosure)**

- `references/lifecycle-and-architecture.md` — 수명주기·저류·ETL/ELT·DW/Lake/Lakehouse·Lambda/Kappa/Medallion
- `references/tooling-playbooks.md` — Airflow·dbt·Kafka·Spark·Iceberg/Lakehouse·Flink 실무 요약·관용구·함정
- `references/quality-and-dataops.md` — 품질 차원·테스트·데이터 계약·관측가능성·거버넌스·DataOps·멱등성/백필

## 에이전트 (Agents)

| 에이전트 | 설명 |
|----------|------|
| `data-engineer` | 요구 정리→수명주기 배치→패턴 선택→도구 선택→산출물 생성→품질·운영 검토의 6단계로 파이프라인/플랫폼을 end-to-end 설계·리뷰·구현하는 자율 에이전트. |

## 빠른 시작

설치 후 아래처럼 요청하면 스킬/에이전트가 활성화됩니다.

```
# 인라인 설계 자문
"이벤트 로그를 실시간 대시보드와 일 배치 리포트에 모두 쓰고 싶어. 아키텍처 설계해줘."

# 리뷰
"이 Airflow DAG / dbt 프로젝트 리뷰해줘. 멱등성·백필 관점 위주로."

# 산출물 생성
"주문 테이블 CDC를 Kafka로 받아 Iceberg 레이크하우스에 적재하는 파이프라인을 설계하고 DAG 초안까지 만들어줘."

# end-to-end (에이전트 위임)
"data-engineer 에이전트로 이 요구사항을 처음부터 끝까지 설계해줘: ..."
```

## 출처

이 플러그인의 지식은 orchwang 위키의 학습 시리즈에서 증류되었습니다.

- Data-Engineering-Essential (수집·저장·처리·오케스트레이션·아키텍처·품질·DataOps)
- Airflow / dbt / Kafka / Spark / Lakehouse(Iceberg) / Stream Processing(Flink) Essential 하위 시리즈

## 라이선스

MIT
