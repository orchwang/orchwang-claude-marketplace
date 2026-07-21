# Changelog

이 문서는 orchwang Plugin Marketplace의 모든 주요 변경 사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
버전 관리는 [Semantic Versioning](https://semver.org/lang/ko/)을 사용합니다.

## [Unreleased]

## [1.5.0] - 2026-07-21

### Added
- `knowledge-librarian` 플러그인 v1.0.0 신규 — 사람이 관리하는 wiki/지식 저장소(md)를 read-only 소스로 지정해 인덱싱·검색하고 전문 서브에이전트에 근거를 전달하는 플러그인 (`local-memory`의 write-out과 반대인 read-in)
  - `librarian` agent: indexer(스캔·파싱·검색) + dispatcher(전문가 위임) 2역할. 소스 read-only 불변식 보장(git commit/push 없음), 인덱스는 현재 repo의 `indexPath`에만 저장
  - `knowledge-index` skill: 소스 스캔·파싱하여 카탈로그 (재)구축. 증분 갱신 / `--force` 전체 재구축, 대형 소스(500+) 경고
  - `knowledge-search` skill: title×3/heading×2/tag·category·series×2/summary×1 가중 랭킹 검색, staleness 경고 병기
  - `knowledge-ask` skill: 검색 후 관련 발췌를 `data-engineer`·`ontology-expert` 등 전문 서브에이전트에 출처와 함께 전달(indexer → specialist)
  - `knowledge-settings` command: 지식 소스 설정 검토·대화형 보완, `indexPath` `.gitignore` 추가 안내
  - references 3종: `source-config.md`(설정 스키마·backend read 매핑·read-only 보장), `index-format.md`(카탈로그 스키마·staleness), `dispatch-contract.md`(전문가 위임 계약)
  - obsidian / filesystem / git 백엔드 read 경로 지원, 다중 소스 지원. Jekyll 블로그(`_posts/`) 검증 예시 포함 — `title`/`tags`/`categories`/`excerpt`/`series`/`published` 파싱, `_site/` 자동 배제
- SDD 스펙 문서 신규: `specs/knowledge-librarian-plugin/`(requirements·specs·plans)

### Changed
- `.claude-plugin/marketplace.json` plugins 배열에 `knowledge-librarian` 등록
- 루트 `README.md` 플러그인 카탈로그에 `knowledge-librarian` 추가

## [1.4.0] - 2026-07-21

### Added
- `data-engineer` 플러그인 v1.0.0 신규 — 데이터 엔지니어링 설계+실무 하이브리드 전문가
  - `data-engineer` skill: 데이터 엔지니어링 수명주기(생성→수집→저장→변환→서빙) + 저류(undercurrents)를 판단 프레임으로, 파이프라인/플랫폼을 설계·리뷰·구현. 산출물 가이드(아키텍처·Airflow DAG·dbt 모델·Kafka/Spark 코드·Iceberg 테이블) 포함
  - `data-engineer` agent: 요구 정리→수명주기 배치→아키텍처 패턴(Batch/Lambda/Kappa/Medallion) 선택→도구 선택→산출물 생성→품질·운영 검토의 6단계 end-to-end 자율 에이전트
  - references 3종(progressive disclosure): `lifecycle-and-architecture.md`, `tooling-playbooks.md`(Airflow·dbt·Kafka·Spark·Iceberg·Flink), `quality-and-dataops.md`
  - 지식 출처: `orchwang.github.io` 위키의 Data-Engineering-Essential 시리즈 및 Airflow/dbt/Kafka/Spark/Lakehouse/Stream-Processing 하위 시리즈
- `ontology-expert` 플러그인 v1.0.0 신규 — 온톨로지·시맨틱 레이어 설계+실무 하이브리드 전문가(FDE 관점)
  - `ontology-expert` skill: "의미 계층 ≠ 물리 데이터 모델"을 원칙으로, 객체·링크·매핑·액션(write-back)·거버넌스를 설계·리뷰·구현. 액션 지향 모델링
  - `ontology-expert` agent: 도메인 이해(액션에서 출발)→객체 도출→링크 설계→매핑·엔티티 해소→액션/write-back→거버넌스의 6단계 FDE 워크플로 자율 에이전트
  - references 3종(progressive disclosure): `modeling-primitives.md`, `mapping-and-actions.md`, `foundations-and-comparisons.md`(지식 그래프·시맨틱 vs 데이터 모델·온톨로지 vs DDD)
  - 지식 출처: `orchwang.github.io` 위키의 Ontology-Essential 시리즈 및 온톨로지 vs DDD 심화편
- SDD 스펙 문서 신규: `specs/data-engineer-plugin/`, `specs/ontology-expert-plugin/`(각 requirements·specs·plans)

### Changed
- `.claude-plugin/marketplace.json` plugins 배열에 `data-engineer`, `ontology-expert` 등록
- 루트 `README.md` 플러그인 카탈로그에 두 전문가 플러그인 추가

## [1.3.0] - 2026-05-13

### Added
- `local-memory` 플러그인 v2.1.0 릴리스 — 저장소 스크립트(specs와 별개 1급 영역) 동기화 지원
  - `/sync-scripts` skill 신규: bash · makefile · django-command 카테고리를 외부기억의 `{repo}/scripts/<카테고리>/` 트리에 동기화. `[<glob-or-path>] [--category bash|makefile|django-command|all]` 인자 지원
  - `references/script-sources.md` 신규: 카테고리 인식 글롭 규칙, 파일명 인코딩 규칙, 자연어 의도 사전(intent dictionary) 단일 레퍼런스
  - `docs/migrations/datamaker-docs-django-commands.md` 신규: datamaker-docs의 루트 평면 `django-commands/` 트리를 `synapse-backend/scripts/django-command/{app}/`로 옮기는 사용자 수동 마이그레이션 가이드
  - `repo-memory` 에이전트에 `scope: specs | scripts | all` 라우팅 계약 추가 — 모호 시 사용자에게 명시 확인
  - 인덱스 노트(`{repo-name}.md`)에 `## Scripts` 섹션 비파괴 lazy-append (Plugin Update Migration). 사용자가 직접 작성한 다른 섹션은 보존
  - `/check-settings`에 "마이그레이션 감사" 절 + Django 휴리스틱(정보성) + 영역별 헬스체크(`[specs]`, `[scripts]` 라벨 분리) 추가

### Changed
- `local-memory` 플러그인 v2.1.0 (호환 유지)
  - 플러그인 표면 텍스트(설명/키워드/README/AGENT/SKILL/command) 백엔드 중립화 — obsidian / filesystem / git 3종을 동등하게 1급으로 노출. README에 `datamaker-docs` git 백엔드 1급 예시 병기
  - `sync-specs`와 `sync-scripts` skill 격리 — 어휘·트리거 단어·`scope` 인자·`[specs]`/`[scripts]` 출력 라벨 분리로 에이전트 라우팅 혼동 차단
  - `plugin.json` keywords 재배치: 영역(`memory`, `repo-context`, `specs`, `scripts`) 우선 + 백엔드(`obsidian`, `filesystem`, `git`) 알파벳 순
  - `/check-settings`의 backend 선택 프롬프트에서 기본값 무음 적용 차단, 3개 옵션을 동등 비중으로 제시
- `.claude-plugin/marketplace.json`의 `local-memory` 버전을 실제 plugin.json(2.1.0)과 일치시키고 description을 백엔드 중립으로 갱신

### Notes
- `.claude/local-memory.json` 설정은 v2.0.0과 100% 호환 — 기존 사용자 데이터(`specs/`, `ideas/`, 인덱스 노트) 무손상
- 신규 `scripts/` 트리와 인덱스 `## Scripts` 섹션은 `/sync-scripts` 최초 호출 시점에만 lazy-create
- `local-memory` v2.0.0(스토리지 백엔드 추상화 — `feat-abstraction-for-local-memory-plugin` PR #2, 2026-03-09)은 마켓플레이스 v1.2.0 시점에 포함되었으나 별도 CHANGELOG 항목이 누락되어 있었음. 본 v1.3.0에서 함께 명시

## [1.2.0] - 2026-03-16

### Added
- `orchwang-general` 플러그인 v1.1.0 릴리스
  - `claude-to-codex-migrator` skill: Claude Code 프로젝트 설정(`.claude/`)을 Codex 호환 스킬 형식으로 변환
    - `.claude/commands/*.md`, `.claude/skills/*.md` → Codex 스킬 디렉토리 변환
    - `P1-P4_rules.md` → code-review 스킬 references 복사
    - `CLAUDE.md` / `AGENTS.md` 호환성 분석
    - 설치된 Claude 플러그인 에셋 → 네임스페이스 Codex 스킬 변환
    - `migrate.py` 스크립트 (dry-run, force, plugins 옵션 지원)
    - `format-mapping.md` 포맷 매핑 레퍼런스 문서
    - `.claude/codex-migration.json` 설정 파일 지원

## [1.1.0] - 2026-03-09

### Added
- `local-memory` 플러그인 v1.1.0 릴리스 — GitHub repo 단위 외부기억을 Obsidian vault에 저장·관리
  - `repo-memory` 에이전트: Pre-flight check, vault 설정, repo name 감지
  - `sync-specs` skill: specs 문서(requirements, specs, plans)를 vault에 동기화
  - `save-idea` skill: 아이디어 메모를 vault에 저장 (태그, 중복 확인 지원)
  - `check-settings` command: 환경 및 설정 항목 검토, 누락 시 대화형 설정 안내
  - `kepano/obsidian-skills` 플러그인 의존성 연동
- `local-memory` 플러그인 SDD 문서 작성 (`specs/create-local-memory-plugin/`)
- `.claude-plugin/marketplace.json` 마켓플레이스 플러그인 목록 파일 추가

### Changed
- vault 저장 경로를 `{directory}/{repo-name}/` 구조로 변경 (`local-memory.directory` 설정 추가)
- `check-settings`를 skill에서 command로 변경
- 설정 파일을 `.claude/local-memory.json`으로 분리

### Fixed
- `marketplace.json` 누락으로 인한 플러그인 설치 불가 오류 해결
- `marketplace.json` source 경로 형식 수정 (`./` 접두사 추가)
- `plugin.json` 미지원 키(`dependencies`, `skills`, `agents`) 제거로 스키마 오류 해결

## [1.0.0] - 2026-03-03

### Added
- 마켓플레이스 초기 구성 완료
- `.claude-plugin/plugin.json` 마켓플레이스 메타데이터 생성
- `plugins/` 디렉토리 구조 도입
- `orchwang-general` 플러그인 스켈레톤 등록 (v1.0.0)
- `AGENTS.md` 저장소 가이드라인 작성
- `docs/CONTRIBUTING.md` 기여 가이드 작성

### 등록된 플러그인

| 플러그인 | 버전 | 설명 |
|---------|------|------|
| orchwang-general | 1.0.0 | 범용 Claude Code 플러그인 |
