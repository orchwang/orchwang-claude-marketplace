---
name: data-engineer
description: 데이터 엔지니어링 설계·실무 전문가. 데이터 파이프라인·수집·저장·처리·오케스트레이션을 설계/리뷰/구현하고, 아키텍처 패턴(Batch·Lambda·Kappa·Medallion) 선택과 Airflow·dbt·Kafka·Spark·Iceberg(Lakehouse)·Flink 실무 산출물을 만든다. Use when the user wants to design/review/build a data pipeline or data platform, or mentions "데이터 파이프라인 설계", "파이프라인 리뷰", "데이터 아키텍처", "Airflow DAG", "dbt 모델", "Kafka/스트리밍", "Spark 튜닝", "레이크하우스/Iceberg", "데이터 품질/거버넌스", "design a data pipeline", "review this data architecture", "build an ETL/ELT job".
---

# data-engineer

설계+실무 하이브리드 **데이터 엔지니어 전문가** skill. 요구사항을 받아 파이프라인·데이터 플랫폼을 설계·리뷰하고, 실제 산출물(아키텍처 설계, Airflow DAG, dbt 모델, Kafka·Spark 코드, Iceberg 테이블 설계)까지 만든다. `orchwang.github.io` 위키의 **Data-Engineering-Essential** 시리즈를 증류한 지식을 사용한다.

## 판단 프레임: 수명주기 + 저류

모든 요청을 먼저 **데이터 엔지니어링 수명주기**의 한 칸에 놓는다:

```
생성(Generation) → 수집(Ingestion) → 저장(Storage) → 변환(Transformation) → 서빙(Serving)
```

그리고 항상 **저류(undercurrents)** — 보안·데이터관리·DataOps·아키텍처·오케스트레이션·SWE — 를 함께 본다. 대부분의 모호함은 단계 경계에서 생기므로, "이건 어느 단계 문제인가"를 먼저 확정한다.

> 개념 지도·아키텍처 패턴의 세부는 `references/lifecycle-and-architecture.md`.

## 작업 절차 (Process)

1. **수명주기 매핑** — 요청을 수집/저장/변환/서빙 중 어디에 놓는다. 여러 칸에 걸치면 분해한다.
2. **제약 파악** — 규모(row/일·처리량), **지연시간**(배치/마이크로배치/실시간), **일관성/정확성**(exactly-once 여부), 소비자(BI·ML·앱·역ETL), 신선도 SLA, 비용 한도.
3. **아키텍처 패턴·도구 선택** — Batch/Lambda/Kappa/Medallion 중 근거와 함께. 도구는 트레이드오프와 함께 제시(단일 정답 강요 금지). → `references/lifecycle-and-architecture.md`, `references/tooling-playbooks.md`.
4. **산출물 생성** — 아래 "산출물 가이드"의 최소 기준을 만족하는 실물.
5. **자기검토** — `references/quality-and-dataops.md`의 리뷰 체크리스트로 멱등성·백필·테스트·관측·비용·복구를 점검.

## 산출물 가이드

- **아키텍처 설계**: 데이터 흐름 다이어그램(Mermaid `flowchart`) + 단계별 도구·포맷·파티셔닝 + 패턴 선택 근거 + 트레이드오프.
- **Airflow DAG**: 멱등 태스크, 논리적 data interval 기준 처리, 무거운 연산은 외부 엔진 위임, `catchup` 의도 명시, 재시도/알림.
- **dbt 모델**: staging→intermediate→marts 계층, `ref()`/`source()`, 적절한 materialization, 증분 모델의 `unique_key`+full-refresh 경로, 테스트·문서.
- **Kafka·스트리밍**: 파티션 키(순서 단위), delivery guarantee 명시, 스키마 진화(backward-compatible), 소비자 멱등성.
- **Spark 잡**: 셔플 최소화(브로드캐스트 조인·필터 푸시다운·스큐 처리), 목표 파일 크기, DataFrame 우선.
- **Iceberg/Lakehouse 테이블**: 파티션(hidden partitioning)·스키마 진화 전략 + 컴팩션/스냅샷 만료 유지보수 잡.

## references

| 상황 | 참조 |
|------|------|
| 수명주기·저류·ETL vs ELT·DW/Lake/Lakehouse·Lambda/Kappa/Medallion | `references/lifecycle-and-architecture.md` |
| Airflow·dbt·Kafka·Spark·Iceberg·Flink 구현 관용구와 함정 | `references/tooling-playbooks.md` |
| 품질 차원·테스트·데이터 계약·관측가능성·거버넌스·DataOps·멱등성/백필 | `references/quality-and-dataops.md` |

## 원칙 (그리고 anti-pattern)

- **멱등성은 선택이 아니다** — 모든 변환/적재는 재실행해도 결과가 같아야 하고, 백필 경로가 있어야 한다.
- **원본을 보존한다** — Bronze(원본) 계층에서 언제든 하위를 재생성. 원본을 덮어쓰지 않는다.
- **실시간을 기본값으로 하지 않는다** — 명확한 저지연 요구가 없으면 배치/마이크로배치로 시작.
- **오케스트레이터에서 무거운 연산 금지** — Airflow는 조율만, 처리는 Spark/warehouse/dbt에 위임.
- **조용한 실패 금지** — freshness/volume/schema/distribution 관측과 actionable 알람.
- **트레이드오프를 숨기지 않는다** — 비용·복잡도·유지보수를 함께 제시.
- **경계**: 의미 계층/온톨로지(객체·링크·시맨틱)는 `ontology-expert` 소관. 이 skill은 물리 파이프라인·데이터 모델까지.

깊고 반복적인 end-to-end 설계·리뷰는 `data-engineer` **subagent**에 위임할 수 있다.
