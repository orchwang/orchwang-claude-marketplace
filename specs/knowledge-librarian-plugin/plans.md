# Plans: knowledge-librarian plugin

> Created: 2026-07-21
> Updated: 2026-07-21 (Step 1–10 구현 완료)
> Status: Implemented (Step 11 라이브 검증 대기)
> Requirements: [requirements.md](./requirements.md)
> Specs: [specs.md](./specs.md)

## Overview

`knowledge-librarian`은 사람이 관리하는 wiki/지식 저장소를 **read-only 지식 소스**로 지정하고, indexer 에이전트가 이를 카탈로그화·검색하여 다른 전문 서브에이전트에게 근거로 전달하는 신규 플러그인이다. `local-memory`(write-out)와 성격이 반대이므로 별도 플러그인으로 신설하되, backend 추상화·전용 설정·agent/skill/references 구조는 재사용한다.

구현은 의존 순서대로 **레퍼런스 → 에이전트 → 명령어 → 스킬 → 패키지/문서 → 마켓플레이스 등록 → 검증**의 흐름을 따른다. 모든 변경은 마크다운 spec 중심이며 실행 코드 변경은 없다.

### Open Questions 결정 (Specs 미해결 항목 처리)

| Open Question | 결정 |
|--------------|------|
| 1. 인덱스 파일 `.gitignore` 추가 | `knowledge-settings`에서 `indexPath`를 현재 repo `.gitignore`에 추가할지 대화형 확인. 기본 권장은 "추가"(인덱스는 로컬 캐시 성격) |
| 2. obsidian staleness 정밀도 | obsidian 소스는 `mtime` 근사가 어려우므로 검색 시 "obsidian 소스는 수동 재인덱싱 권장" 경고를 상시 병기. staleness 강제 차단은 하지 않음 |
| 3. `roots` 미지정 대형 wiki 성능 | 최초 인덱싱에서 대상 문서 수가 임계값(기본 500) 초과 시 경고하고 `roots`/`exclude` 축소를 권고. 중단은 하지 않음 |
| 4. `knowledge-ask` 발췌 상한 | 상위 문서 최대 5개 × 문서당 발췌 최대 ~1500자. 초과 시 관련 heading 섹션 우선 절삭 |

## Prerequisites

- 본 repo(`orchwang-claude-marketplace`)에서 작업
- `plugins/local-memory/references/backend-operations.md` 참조 가능 (read 매핑 차용 원본)
- 마켓플레이스에 `data-engineer`, `ontology-expert` 플러그인 존재 확인 (dispatch 대상)
- 작성·편집 시 한국어, 2-space YAML 들여쓰기, kebab-case 파일명 준수 (AGENTS.md)
- 외부 의존성 추가 없음 (obsidian 소스 사용 시에만 obsidian 플러그인 의존)

## Implementation Steps

### Step 1: `references/source-config.md` 생성

- **Goal**: 설정 스키마 · backend read 매핑 · read-only 보장을 단일 레퍼런스로 둔다.
- **Specs Reference**: specs.md "설정 스키마", "Backend read 매핑"
- **Files**: `plugins/knowledge-librarian/references/source-config.md` — Create
- **Details**:
  - 설정 필드 표(FR-1) + 다중 소스 예시(FR-7)
  - filesystem/git/obsidian READ·SCAN·EXISTS·MTIME 매핑 표. **CREATE/commit/push는 명시적으로 "미포함(read-only)"이라고 기재** (FR-5)
  - `local-memory`의 git 백엔드(write)와 정반대임을 경고 박스로 명시

### Step 2: `references/index-format.md` 생성

- **Goal**: 카탈로그 JSON 스키마와 파싱·staleness·증분 규칙 정의.
- **Specs Reference**: specs.md "인덱스(카탈로그) 스키마"
- **Files**: `plugins/knowledge-librarian/references/index-format.md` — Create
- **Details**:
  - 엔트리 필드 표, title/summary 우선순위, staleness 판정식, 증분 갱신 알고리즘
  - 대형 wiki 임계값(500) 경고 규칙(Open Q3 결정)

### Step 3: `references/dispatch-contract.md` 생성

- **Goal**: 전문가 서브에이전트 위임 계약 정의.
- **Specs Reference**: specs.md "디스패치 계약", FR-4
- **Files**: `plugins/knowledge-librarian/references/dispatch-contract.md` — Create
- **Details**:
  - 페이로드 구조 `{ question, evidence[], instructions }`
  - 대상 에이전트 검증 규칙(실재 에이전트 한정), 발췌 상한(Open Q4 결정)
  - 출처 라벨링 규약(`[source] path`)

### Step 4: `agents/librarian/AGENT.md` 생성

- **Goal**: indexer + dispatcher 역할의 에이전트 playbook.
- **Specs Reference**: specs.md "`librarian` 에이전트 계약"
- **Files**: `plugins/knowledge-librarian/agents/librarian/AGENT.md` — Create
- **Details**:
  - Pre-flight(설정 존재, 소스 접근성, roots 검사)
  - 소스 backend 확정 규칙(소스별 > 전역)
  - `--source` scope 처리, `[librarian]` 출력 라벨
  - read-only 불변식 명시(소스에 절대 쓰지 않음)
  - 세 skill(index/search/ask)에 컨텍스트 제공 방식

### Step 5: `skills/knowledge-index/SKILL.md` 생성

- **Goal**: 카탈로그 (재)구축 스킬.
- **Specs Reference**: specs.md "knowledge-index", FR-2·FR-8
- **Files**: `plugins/knowledge-librarian/skills/knowledge-index/SKILL.md` — Create
- **Details**:
  - 인자 `[--source name] [--force]`, 증분 vs 전체 재구축
  - SCAN → 파싱 → `indexPath` 기록(소스 미기록), 보고 형식(신규/변경/삭제 건수)
  - 트리거 어휘: "지식 인덱싱", "wiki 인덱스", "knowledge index", "카탈로그 갱신"

### Step 6: `skills/knowledge-search/SKILL.md` 생성

- **Goal**: 카탈로그 검색 스킬.
- **Specs Reference**: specs.md "knowledge-search", FR-3
- **Files**: `plugins/knowledge-librarian/skills/knowledge-search/SKILL.md` — Create
- **Details**:
  - 인자 `"질의" [--source name] [--limit N]`
  - 가중 랭킹(title×3/heading×2/tag×2/summary×1), staleness 경고 병기
  - 인덱스 부재 시 `/knowledge-index` 안내 후 중단
  - 트리거 어휘: "지식 검색", "wiki 검색", "knowledge search", "문서 찾아줘"

### Step 7: `skills/knowledge-ask/SKILL.md` 생성

- **Goal**: 검색 + 전문가 서브에이전트 디스패치 스킬 (핵심 기능).
- **Specs Reference**: specs.md "knowledge-ask", "디스패치 계약", FR-4
- **Files**: `plugins/knowledge-librarian/skills/knowledge-ask/SKILL.md` — Create
- **Details**:
  - 인자 `"질문" [--to agent] [--source name]`
  - 검색 → 발췌 READ → 대상 에이전트 결정(미지정 시 AskUserQuestion) → Agent 도구 호출 → 응답+출처 보고
  - 발췌 상한 규칙, 대상 에이전트 실재성 검증
  - 트리거 어휘: "지식 기반으로 물어봐", "wiki 근거로 ...에게 물어봐", "knowledge ask"

### Step 8: `commands/knowledge-settings.md` 생성

- **Goal**: 설정 검토·보완 명령 (FR-9).
- **Specs Reference**: requirements.md FR-9, FR-10
- **Files**: `plugins/knowledge-librarian/commands/knowledge-settings.md` — Create
- **Details**:
  - 설정 존재·필수 항목·소스 접근성·roots 존재 점검
  - 누락 항목 AskUserQuestion 보완 후 저장
  - `indexPath` `.gitignore` 추가 여부 확인(Open Q1 결정)
  - `local-memory.json`과 분리됨을 안내

### Step 9: `plugin.json` + `README.md` 생성

- **Goal**: 패키징 필수 산출물 (AGENTS.md "Plugin Documentation Requirements").
- **Files**:
  - `plugins/knowledge-librarian/plugin.json` — Create
  - `plugins/knowledge-librarian/README.md` — Create
- **Details**:
  - `plugin.json`: name `knowledge-librarian`, version `1.0.0`, 한국어 description, keywords(`knowledge`, `wiki`, `librarian`, `indexer`, `dispatch`, `read-only`)
  - README 섹션: 개요 / 설치 / 설정 / 명령어 / 스킬 / 에이전트 / 폴더·인덱스 구조 / **local-memory와의 차이(write-out vs read-in)**(FR-10) / 라이선스

### Step 10: 마켓플레이스 등록 + 문서 갱신

- **Goal**: 마켓플레이스와 루트 문서에 신규 플러그인 반영.
- **Files**:
  - `.claude-plugin/marketplace.json` — Edit (plugins 배열에 `knowledge-librarian` 추가, marketplace version bump)
  - `README.md`(루트) — Edit (플러그인 목록에 추가)
  - `CHANGELOG.md` — Edit (Unreleased에 신규 플러그인 항목 추가)
- **Details**:
  - marketplace.json에 name/source/description/version 엔트리 추가
  - 루트 README 플러그인 표에 한 줄 추가

### Step 11: 라이브 검증

- **Goal**: 실제 wiki 저장소로 end-to-end 동작 확인.
- **Details**:
  - filesystem/git 소스로 `.claude/knowledge-librarian.json` 작성 → `/knowledge-settings` 점검
  - `/knowledge-index` → 인덱스가 `indexPath`에만 생성되고 **소스는 변경 없음**(git status clean) 확인 (FR-5)
  - `/knowledge-search "..."` 랭킹·발췌 확인
  - `/knowledge-ask "..." --to data-engineer` → 근거 첨부 위임·출처 보고 확인 (FR-4)
  - staleness: 소스 문서 수정 후 검색 시 경고 병기 확인 (FR-8)

## Testing Strategy

- 자동 테스트 스위트 없음(AGENTS.md) — Claude Code에서 각 명령을 실제 실행하여 검증
- read-only 불변식 회귀 검사: 모든 스킬 실행 후 소스 저장소 `git status`/파일 mtime 불변 확인
- 다중 소스: filesystem + obsidian 혼합 설정으로 `--source` 스코핑 확인

## Rollback / Safety

- 신규 플러그인 추가이므로 기존 `local-memory` 및 사용자 데이터에 영향 없음
- 소스 저장소는 read-only — 롤백 대상이 되는 write가 없음
- 문제 시 `.claude-plugin/marketplace.json`에서 엔트리 제거로 비활성화

## Dependencies & Sequencing

```
Step 1,2,3 (references, 병렬 가능)
    → Step 4 (agent, references 참조)
        → Step 5,6,7 (skills, agent+references 참조)
            → Step 8 (command)
                → Step 9 (package)
                    → Step 10 (marketplace/docs)
                        → Step 11 (검증)
```
