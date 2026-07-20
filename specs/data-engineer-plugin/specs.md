# Specs: data-engineer plugin

> Created: 2026-07-20
> Status: Draft

## 1. 패키지 구조

```
plugins/data-engineer/
  plugin.json
  README.md
  skills/
    data-engineer/
      SKILL.md
      references/
        lifecycle-and-architecture.md
        tooling-playbooks.md
        quality-and-dataops.md
  agents/
    data-engineer/
      AGENT.md
```

## 2. plugin.json

```json
{
  "name": "data-engineer",
  "version": "1.0.0",
  "description": "데이터 엔지니어링 설계·실무 전문가 — 수명주기(수집·저장·처리·오케스트레이션)·아키텍처 패턴·Airflow/dbt/Kafka/Spark/Iceberg 실무를 설계 자문과 산출물 생성으로 지원",
  "author": { "name": "orchwang" },
  "homepage": "https://github.com/orchwang/orchwang-claude-marketplace",
  "repository": "https://github.com/orchwang/orchwang-claude-marketplace.git",
  "license": "MIT",
  "keywords": ["data-engineering", "data-pipeline", "airflow", "dbt", "kafka", "spark", "lakehouse", "iceberg", "dataops"]
}
```

## 3. SKILL.md 사양

### 3.1 Frontmatter

- `name: data-engineer`
- `description`: 무엇을 하는지 + 트리거 문구(한/영). 예: "데이터 파이프라인·수집·저장·처리·오케스트레이션을 설계/리뷰/구현… Use when … '데이터 파이프라인 설계', '파이프라인 리뷰', 'Airflow DAG', 'dbt 모델', 'design a data pipeline', 'review this data architecture'."

### 3.2 본문 섹션

1. **역할 정의** — 설계+실무 하이브리드 데이터 엔지니어. 무엇을 도와주는가.
2. **판단 프레임: 데이터 엔지니어링 수명주기 + 저류** — 모든 요청을 생성→수집→저장→변환→서빙의 어느 칸에 놓고, 저류(보안·데이터관리·DataOps·아키텍처·오케스트레이션·SWE)를 항상 함께 본다.
3. **작업 절차(Process)** — (1) 요청을 수명주기 단계로 매핑 (2) 제약·규모·지연시간·일관성 요구 파악 (3) 아키텍처 패턴/도구 선택 (4) 산출물 생성 (5) 품질·운영·비용 관점 자기검토.
4. **산출물 가이드** — 아키텍처 설계 문서 / Airflow DAG / dbt 모델·테스트 / Kafka·Spark 코드 / Iceberg 테이블 설계 각각의 최소 기준.
5. **references 안내** — 언제 어떤 참조 문서를 여는지.
6. **원칙(anti-patterns 포함)** — 멱등성·재처리·스키마 진화·비용/성능 트레이드오프를 명시적으로 다룬다.

### 3.3 references 매핑

| 상황 | 참조 |
|------|------|
| 수명주기·아키텍처 패턴·ETL vs ELT·Lakehouse 개념 | `references/lifecycle-and-architecture.md` |
| Airflow/dbt/Kafka/Spark/Iceberg/Flink 구현 관용구 | `references/tooling-playbooks.md` |
| 품질·테스트·데이터 계약·관측가능성·거버넌스·DataOps | `references/quality-and-dataops.md` |

## 4. AGENT.md 사양

### 4.1 Frontmatter

- `name: data-engineer`
- `description`: end-to-end 파이프라인 설계·리뷰·구현 자율 에이전트임을 명시 + 트리거.

### 4.2 워크플로 (위키 8단계 사고법 반영)

1. **요구 정리** — 원천·목적지·소비자·규모(row/일, 처리량)·지연시간(배치/마이크로배치/실시간)·일관성/정확성 요구·SLA.
2. **수명주기 배치** — 각 요구를 생성→수집→저장→변환→서빙에 배치.
3. **아키텍처 패턴 선택** — Batch / Lambda / Kappa / Med((Bronze·Silver·Gold) Medallion) 중 근거와 함께 선택.
4. **도구 선택** — 수집(Kafka/CDC/배치), 저장(Lakehouse·Iceberg/DW), 처리(Spark/dbt/Flink), 오케스트레이션(Airflow) 중 트레이드오프와 함께.
5. **산출물 생성** — 설계 다이어그램(Mermaid) + 핵심 코드(DAG/모델/잡) + 테이블/스키마 설계.
6. **품질·운영 검토** — 멱등성·백필·데이터 품질 테스트·관측가능성·비용·실패 복구 관점의 자기 리뷰.

### 4.3 규칙

- 요구가 불충분하면 핵심 축(규모·지연시간·일관성·소비자)에 대해 가정을 명시하거나 질문한다.
- 항상 트레이드오프를 함께 제시한다(단일 정답 강요 금지).
- skill의 references를 지식원으로 재사용한다.

## 5. README.md 필수 섹션

개요 / 설치 / 스킬 / 에이전트 / 빠른 시작(예시 프롬프트) / 출처(위키 시리즈) / 라이선스.

## 6. 등록 변경

- `.claude-plugin/marketplace.json` plugins 배열에 `data-engineer` 추가
- 루트 `README.md` 플러그인 카탈로그 표·설명 추가
- `CHANGELOG.md`에 신규 플러그인 기록
- 마켓플레이스 루트 `plugin.json` version 마이너 bump
