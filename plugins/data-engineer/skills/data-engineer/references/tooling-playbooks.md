# Reference: 도구별 실무 플레이북

각 도구를 "무엇을 푸는가 · 핵심 개념 · 실무 관용구 · 흔한 함정" 순으로 요약한다. 튜토리얼이 아니라 **설계·리뷰 시 바로 쓰는 체크리스트**다.

## 1. Airflow — 오케스트레이션

**무엇을 푸는가**: 태스크 간 의존성·스케줄·재시도·백필을 코드(DAG)로 관리.

**핵심 개념**
- **DAG / Operator / Task / TaskInstance**: DAG는 워크플로 정의, Operator는 작업 단위 템플릿, Task는 인스턴스화된 노드.
- **Scheduler / Executor**: 스케줄러가 실행할 태스크를 판단, Executor(Local·Celery·Kubernetes)가 실제 실행.
- **XCom / TaskFlow API**: 태스크 간 소량 데이터 전달. TaskFlow(`@task`)로 파이썬 함수를 태스크로.
- **Sensor / Deferrable Operator**: 조건 대기. Deferrable은 유휴 대기를 트리거러로 넘겨 워커 슬롯 낭비 제거.

**실무 관용구**
- 태스크는 **멱등(idempotent)**하게: 같은 execution_date로 재실행해도 결과 동일.
- **execution_date / data interval** 기준으로 파티션을 처리(현재 시각이 아니라 논리적 구간).
- 무거운 연산은 Airflow가 아니라 **외부 엔진(Spark·dbt·warehouse)에 위임**하고 Airflow는 조율만.

**흔한 함정**
- Airflow 워커에서 대용량 처리(메모리 폭발). → 위임.
- `catchup=True` 방치로 대량 백필 폭주. 의도 없으면 `catchup=False`.
- XCom으로 대용량 전달(메타DB 부하). 큰 데이터는 스토리지 경유.

## 2. dbt — 애널리틱스 엔지니어링(변환/ELT)

**무엇을 푸는가**: 웨어하우스/레이크하우스 안에서 SQL 변환을 소프트웨어 공학적으로(버전·테스트·문서·의존성) 관리.

**핵심 개념**
- **model / `ref()` / `source()`**: 모델은 SELECT 하나 = 테이블/뷰. `ref`로 모델 의존성, `source`로 원천 선언. 의존성에서 DAG 자동 생성.
- **materialization**: `view` / `table` / `incremental` / `ephemeral`.
- **incremental / snapshot**: 증분 적재(신규/변경만), snapshot은 SCD Type-2 이력.
- **tests / documentation**: `not_null`·`unique`·`relationships`·`accepted_values` + 커스텀. 스키마 YAML에 문서.
- **macros / Jinja**: 재사용 SQL 로직. **semantic layer / metrics**: 지표 정의를 코드로 단일화.
- **packages / CI**: 패키지 재사용, slim CI(`state:modified`)로 변경분만 빌드·테스트.

**실무 관용구**
- 계층: **staging(원천 1:1 정리) → intermediate(조인·가공) → marts(비즈니스)**. Medallion과 대응.
- 증분 모델엔 **`unique_key` + 지연 도착(late-arriving) 처리** 고려.
- 모든 원천에 `source freshness`, 핵심 모델에 테스트를 건다.

**흔한 함정**
- 증분 모델의 백필/재빌드 로직 부재. `--full-refresh` 경로를 항상 확보.
- 뷰 남발로 런타임 폭증 / 테이블 남발로 스토리지·빌드시간 폭증. materialization을 의식적으로.

## 3. Kafka — 분산 로그 / 수집·스트리밍 백본

**무엇을 푸는가**: 불변·순서 보장(파티션 내) 로그로 시스템 간 데이터를 비동기·확장가능하게 흘림.

**핵심 개념**
- **topic / partition / offset**: 병렬성·순서의 단위는 파티션. 순서는 파티션 내에서만 보장.
- **producer / consumer / consumer group**: 그룹으로 파티션을 나눠 병렬 소비. 리밸런싱 이해 필수.
- **delivery guarantee**: at-most / at-least / exactly-once. 멱등 프로듀서 + 트랜잭션으로 EOS.
- **schema registry**: Avro/Protobuf 스키마 버전·호환성(backward/forward) 관리.
- **Kafka Connect / CDC**: 소스·싱크 커넥터. Debezium 등으로 DB 변경 캡처(CDC) → 로그화.
- **Kafka Streams**: 토픽→토픽 스트림 처리(상태·윈도우·조인).

**실무 관용구**
- 파티션 키로 **순서가 필요한 단위(예: user_id)**를 묶는다.
- 소비자는 **멱등 처리** 또는 오프셋 커밋 전략으로 중복에 견디게.
- 스키마는 **backward-compatible 진화**를 기본으로(컨슈머 먼저 배포).

**흔한 함정**
- 파티션 수 과소 → 처리량 한계 / 과다 → 리밸런싱·메타 부하.
- exactly-once를 "쉽게" 가정. 종단 간 EOS는 프로듀서·브로커·컨슈머·싱크가 모두 협조해야 성립.

## 4. Spark — 분산 처리 엔진

**무엇을 푸는가**: 대규모 데이터의 분산 배치/스트리밍 처리(인메모리).

**핵심 개념**
- **driver / executor**: 드라이버가 계획·조율, executor가 태스크 실행. 파티션 = 병렬 단위.
- **RDD / DataFrame / Dataset**: 실무는 DataFrame(카탈리스트 최적화 수혜). RDD는 저수준.
- **Catalyst / Tungsten / AQE**: 쿼리 최적화·코드젠·적응형 실행(런타임 통계로 조인/파티션 조정).
- **shuffle / partitioning**: 셔플은 최대 비용원. 조인·집계·`repartition`이 유발.
- **PySpark UDF / pandas API**: UDF는 직렬화 비용 큼 → 내장 함수·pandas UDF 우선.
- **Structured Streaming**: 마이크로배치(또는 연속) 스트림, 워터마크·상태.
- **Iceberg/Delta on Spark**: 레이크하우스 테이블 읽기/쓰기 엔진으로 자주 결합.

**실무 관용구**
- **셔플 최소화**: 브로드캐스트 조인(작은 테이블), 필터 푸시다운, 적절한 파티션 수, 스큐 처리(salting/AQE skew join).
- 파일 크기 목표: 조각(small files) 회피, 128MB~1GB 수준으로 컴팩션.
- 캐시는 재사용이 확실할 때만.

**흔한 함정**
- 파티션 스큐로 특정 태스크만 폭주. AQE·salting.
- collect()로 드라이버 OOM. 대용량은 write로.

## 5. Lakehouse / Apache Iceberg — 개방형 테이블 포맷

**무엇을 푸는가**: 오브젝트 스토리지(S3 등) 위 파일에 **ACID·스키마 진화·타임트래블**을 부여해 웨어하우스급 신뢰성을 레이크에서 실현.

**핵심 개념**
- **왜 개방형 테이블 포맷인가**: "파일 나열" 방식(Hive)의 문제(원자성·동시성·스키마 변경·작은 파일)를 메타데이터 계층으로 해결.
- **메타데이터 구조**: metadata file → manifest list → manifest → data files. 스냅샷 단위 커밋.
- **ACID / 스냅샷 / 타임트래블**: 스냅샷 격리, 특정 시점 조회·롤백.
- **파티션 진화 / 스키마 진화**: 데이터 재작성 없이 파티션·컬럼 변경(hidden partitioning).
- **컴팩션·유지보수**: 작은 파일 병합, 매니페스트 재작성, 오래된 스냅샷 만료.
- **REST 카탈로그 / 거버넌스**: 카탈로그로 테이블 커밋·권한 관리.
- **포맷 비교**: Iceberg vs Delta vs Hudi — 진화·엔진 호환·커뮤니티 트레이드오프.

**실무 관용구**
- **hidden partitioning**으로 쿼리 시 파티션 컬럼 노출 없이 프루닝.
- 정기 **컴팩션 + 스냅샷 만료**를 유지보수 잡으로 스케줄(Airflow).
- 스키마 진화는 **additive 우선**, 파괴적 변경은 신중히.

**흔한 함정**
- 유지보수 잡 부재 → 작은 파일·오래된 스냅샷 누적으로 성능·비용 악화.
- 카탈로그/엔진 조합의 기능 격차(모든 엔진이 모든 기능을 동일 지원하지 않음).

## 6. Stream Processing / Apache Flink

**무엇을 푸는가**: 진짜 저지연·상태 기반 스트림 처리(이벤트 타임·윈도우·정확히 한 번).

**핵심 개념**
- **이벤트 타임 vs 처리 타임 / 워터마크**: 늦게 도착한 이벤트를 이벤트 시각 기준으로 올바른 윈도우에 배치.
- **윈도우**: tumbling / sliding / session.
- **상태(state) / 체크포인트**: 관리형 상태 + 주기적 체크포인트로 장애 복구·exactly-once.
- **Flink vs Spark Structured Streaming**: Flink는 네이티브 스트리밍(레코드 단위·저지연), Spark는 마이크로배치 기반.

**실무 관용구**
- 지연 허용(allowed lateness)과 워터마크 전략을 명시적으로 설계.
- 상태 크기·TTL 관리(무한 상태 방지).

**흔한 함정**
- 워터마크 오설정으로 윈도우가 영영 안 닫히거나 늦은 데이터 유실.
- 상태 폭발(키 카디널리티·TTL 부재).

## 도구 선택 빠른 결정

| 필요 | 1순위 |
|------|-------|
| 스케줄·의존성·백필 | Airflow |
| 웨어하우스 내 SQL 변환·모델링·테스트 | dbt |
| 시스템 간 이벤트 백본·CDC | Kafka |
| 대규모 배치/ETL 분산 처리 | Spark |
| 레이크에 ACID·타임트래블 | Iceberg(레이크하우스) |
| 저지연·상태 기반 실시간 | Flink |
