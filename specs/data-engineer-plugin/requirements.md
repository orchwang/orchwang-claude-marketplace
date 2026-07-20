# Requirements: data-engineer plugin

> Created: 2026-07-20
> Status: Draft
> Ticket: N/A

## Overview

`orchwang.github.io` 위키의 **Data-Engineering-Essential** 시리즈(정의·역사 → 수집·저장·처리·오케스트레이션 → 아키텍처·사례 → 품질·거버넌스·DataOps, 그리고 Airflow·dbt·Kafka·Spark·Lakehouse(Iceberg)·Stream Processing(Flink) 심화 하위 시리즈)를 하나의 **재사용 가능한 전문가 플러그인**으로 증류한다.

산출물은 Claude Code 마켓플레이스(`orchwang-marketplace`)에 배포 가능한 `data-engineer` 플러그인으로, **설계+실무 하이브리드** 성격의 데이터 엔지니어 전문가다. 설계 자문(아키텍처 리뷰·기술 선택·트레이드오프)과 실제 산출물 생성(파이프라인 설계, Airflow DAG, dbt 모델, Kafka·Spark 코드, Iceberg 테이블 설계)을 모두 수행한다.

## Goals

- [ ] 위키 Data-Engineering 시리즈의 지식을 progressive disclosure 구조(SKILL + references)로 증류
- [ ] 인라인 질의응답·설계 자문에 반응하는 `data-engineer` **skill** 구현
- [ ] 파이프라인을 end-to-end로 설계·리뷰·구현하는 `data-engineer` **subagent(agent)** 구현
- [ ] 마켓플레이스 규약(plugin.json · README 필수 섹션 · CHANGELOG · kebab-case)을 준수한 배포 가능 패키지
- [ ] `orchwang-general`/`local-memory`와 동일한 문서 품질·톤(한국어) 유지

## Functional Requirements

### FR-1: data-engineer skill

- **Description**: 데이터 엔지니어링 설계·구현 질문에 인라인으로 반응하는 skill. 데이터 엔지니어링 수명주기(생성→수집→저장→변환→서빙)와 저류(보안·데이터관리·DataOps·아키텍처·오케스트레이션·SWE)를 뼈대로 삼아, 요청을 수명주기의 어느 단계로 매핑하고 적절한 패턴·도구·코드로 답한다.
- **Acceptance Criteria**:
  - [ ] `skills/data-engineer/SKILL.md`가 존재하고 frontmatter(name·description)에 한국어+영어 트리거 문구를 포함한다
  - [ ] 수명주기·저류를 판단 프레임으로 사용하는 절차(Process)를 명시한다
  - [ ] 깊은 주제는 `references/`로 분리(progressive disclosure)한다
  - [ ] 산출물 유형(아키텍처 설계·DAG·dbt 모델·스트리밍 잡·테이블 설계)별 실무 지침을 담는다

### FR-2: data-engineer subagent

- **Description**: 요구사항을 받아 파이프라인/데이터 시스템을 end-to-end로 설계·리뷰·구현하는 자율 에이전트. 위키 8단계(사례별 파이프라인 설계) 사고법을 따른다: 요구 정리 → 수명주기 배치 → 아키텍처 패턴 선택(Lambda/Kappa/Medallion) → 도구 선택 → 산출물 생성 → 품질·운영 관점 검토.
- **Acceptance Criteria**:
  - [ ] `agents/data-engineer/AGENT.md`가 존재하고 frontmatter(name·description)를 갖는다
  - [ ] 설계 워크플로(요구 정리→배치→패턴→도구→산출물→검토)를 단계로 명시한다
  - [ ] 불충분한 요구사항일 때 가정을 명시하거나 질문하도록 규정한다
  - [ ] skill의 references를 공유 지식원으로 참조한다

### FR-3: 도메인 references (progressive disclosure)

- **Description**: SKILL 본문을 가볍게 유지하고 깊은 지식은 참조 문서로 분리한다.
- **Acceptance Criteria**:
  - [ ] `references/lifecycle-and-architecture.md` — 수명주기·저류·ETL/ELT·DW/Lake/Lakehouse·Lambda/Kappa/Medallion
  - [ ] `references/tooling-playbooks.md` — Airflow·dbt·Kafka·Spark·Iceberg/Lakehouse·Flink 실무 요약과 관용구
  - [ ] `references/quality-and-dataops.md` — 데이터 품질 차원·테스트·데이터 계약·관측가능성·거버넌스·DataOps·신뢰성/SLA

### FR-4: 배포 패키징

- **Description**: 마켓플레이스 배포 규약을 만족한다.
- **Acceptance Criteria**:
  - [ ] `plugins/data-engineer/plugin.json` 매니페스트(유효 JSON, 정확한 메타)
  - [ ] `plugins/data-engineer/README.md`가 개요·설치·스킬·에이전트·빠른 시작·라이선스 섹션을 포함
  - [ ] `.claude-plugin/marketplace.json`에 등록, 루트 `README.md` 목록·`CHANGELOG.md` 갱신
  - [ ] 시크릿·로컬 절대경로 미포함, kebab-case 준수

## Non-Functional Requirements

- **문서 언어**: 한국어(코드·기술용어·고유명사는 영어)
- **출처 정합성**: 위키 시리즈의 개념·용어·구조와 상충하지 않는다(증류이지 재창작이 아님)
- **독립성**: 외부 유료 서비스나 비밀정보에 의존하지 않는다(순수 지식·프롬프트 자산)

## Out of Scope

- 위키 포스트 원문의 그대로 복사(요약·증류만 수행)
- 특정 클라우드 벤더 콘솔 자동화나 실제 인프라 프로비저닝
- ontology-expert 플러그인(별도 spec: `ontology-expert-plugin`)
