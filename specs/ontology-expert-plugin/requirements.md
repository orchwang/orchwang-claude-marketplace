# Requirements: ontology-expert plugin

> Created: 2026-07-20
> Status: Draft
> Ticket: N/A

## Overview

`orchwang.github.io` 위키의 **Ontology-Essential** 시리즈(의미 계층의 정의 → 형식 기반·지식 그래프(RDF/OWL·속성 그래프) → 객체 타입·속성 → 링크 타입·관계 → 소스 데이터 매핑·엔티티 해소 → 액션·운영 계층(write-back) → 거버넌스·진화·FDE 워크플로, 그리고 심화편 온톨로지 vs DDD)를 하나의 **재사용 가능한 전문가 플러그인**으로 증류한다.

산출물은 Claude Code 마켓플레이스(`orchwang-marketplace`)에 배포 가능한 `ontology-expert` 플러그인으로, Palantir식 **FDE(Forward Deployed Engineer)** 관점의 **설계+실무 하이브리드** 온톨로지/시맨틱 레이어 전문가다. 의미 계층 설계 자문과 실제 산출물 생성(객체 타입·링크 타입·데이터 매핑·액션/write-back 정의)을 모두 수행한다.

## Goals

- [ ] 위키 Ontology 시리즈의 지식을 progressive disclosure 구조(SKILL + references)로 증류
- [ ] 온톨로지/시맨틱 레이어 설계 질문에 반응하는 `ontology-expert` **skill** 구현
- [ ] 원천 데이터에서 온톨로지를 end-to-end로 설계·리뷰하는 `ontology-expert` **subagent(agent)** 구현
- [ ] 마켓플레이스 규약(plugin.json · README 필수 섹션 · CHANGELOG · kebab-case)을 준수한 배포 가능 패키지

## Functional Requirements

### FR-1: ontology-expert skill

- **Description**: 의미 계층/온톨로지 모델링 질문에 인라인으로 반응하는 skill. "온톨로지 = 데이터 모델이 아니라 그 위의 의미 계층"이라는 핵심 원칙을 뼈대로, 객체·링크·매핑·액션이라는 1급 개념으로 문제를 재구성한다.
- **Acceptance Criteria**:
  - [ ] `skills/ontology-expert/SKILL.md`가 존재하고 frontmatter(name·description)에 한국어+영어 트리거 문구를 포함한다
  - [ ] 의미 계층 vs 물리 데이터 모델 구분을 판단 프레임으로 사용한다
  - [ ] 깊은 주제는 `references/`로 분리(progressive disclosure)한다
  - [ ] 산출물 유형(객체 타입·링크 타입·매핑·액션/write-back·거버넌스)별 실무 지침을 담는다

### FR-2: ontology-expert subagent

- **Description**: 원천 데이터셋/도메인 설명을 받아 온톨로지를 end-to-end로 설계·리뷰하는 자율 에이전트. FDE 워크플로를 따른다: 도메인 이해 → 객체 후보 도출 → 링크 설계 → 백킹 데이터셋 매핑·엔티티 해소 → 액션/write-back 설계 → 거버넌스·진화 관점 검토.
- **Acceptance Criteria**:
  - [ ] `agents/ontology-expert/AGENT.md`가 존재하고 frontmatter(name·description)를 갖는다
  - [ ] FDE 설계 워크플로를 단계로 명시한다
  - [ ] 불충분한 입력일 때 도메인·소스·의사결정을 질문하도록 규정한다
  - [ ] skill의 references를 공유 지식원으로 참조한다

### FR-3: 도메인 references (progressive disclosure)

- **Acceptance Criteria**:
  - [ ] `references/modeling-primitives.md` — 객체 타입·속성·기본키·링크 타입·카디널리티·그래프 탐색
  - [ ] `references/mapping-and-actions.md` — 백킹 데이터셋·엔티티 해소·액션/write-back·운영 계층
  - [ ] `references/foundations-and-comparisons.md` — 지식 그래프(RDF/OWL·속성 그래프)·시맨틱 레이어 vs 데이터 모델·온톨로지 vs DDD·거버넌스/FDE 워크플로

### FR-4: 배포 패키징

- **Acceptance Criteria**:
  - [ ] `plugins/ontology-expert/plugin.json` 매니페스트(유효 JSON)
  - [ ] `plugins/ontology-expert/README.md`가 개요·설치·스킬·에이전트·빠른 시작·라이선스 섹션 포함
  - [ ] `.claude-plugin/marketplace.json`에 등록, 루트 `README.md`·`CHANGELOG.md` 갱신
  - [ ] 시크릿·로컬 절대경로 미포함, kebab-case 준수

## Non-Functional Requirements

- **문서 언어**: 한국어(코드·기술용어·고유명사는 영어)
- **출처 정합성**: 위키 Ontology 시리즈의 개념·용어와 일관
- **독립성**: 특정 벤더(Palantir Foundry 등) 제품에 종속되지 않는 원리 중심 서술(개념 출처로만 언급)

## Out of Scope

- 위키 포스트 원문 그대로 복사
- 특정 온톨로지 편집기/플랫폼 자동화
- data-engineer 플러그인(별도 spec: `data-engineer-plugin`) — 물리 파이프라인/저장/처리 소관
