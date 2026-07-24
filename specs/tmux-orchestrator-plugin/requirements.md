# Requirements: tmux-orchestrator 플러그인

> 상태: **SDD 진행 / 구현 보류** (2026-07-24)

## Overview

여러 tmux 세션·pane 에서 `claude` 가 동시에 실행 중인 환경에서, 하나의 **오케스트레이터 세션**이
실행 중인 claude pane 들을 발견하고 역할(tech-lead / implementer / reviewer 등)을 계획·태깅하여
멀티 에이전트 협업을 수행하도록 표준화하는 Claude Code 플러그인.

오케스트레이터는 pane 을 임의로 점유하지 않고 **제안 → 사용자 승인 → 실행** 게이트를 거친다.
이미 수동으로 쓰이던 `[OPUS-1 ACK]` 류 마커 컨벤션을 자동화·표준화하는 것이 목적이다.

## Goals

- **G1**: 실행 중인 claude pane 을 발견하고 역할·모델·상태를 pane 자체에 각인(tag)한다.
- **G2**: 오케스트레이터가 작업을 SDD 로 분해하고, 필요 역할 수 대비 가용 pane 을 진단해 **제안**한다.
- **G3**: 사용자 승인 후, 워커에게 서브태스크를 dispatch 하고 완료를 감지·수집·통합한다.
- **G4**: 워커별로 **프로파일**(model·effort·permission·budget·fast·behavioral directive)을 지정·혼합한다.
- **G5**: 사람이 개입하는 게이트를 유지해 워커 pane 의 오점유·오배정을 방지한다.
- **G6**: attitude 프리셋(절약/품질/속도 등)으로 옵션 묶음을 한 번에 적용한다.

## Functional Requirements

### FR-1: 에이전트 discover
- `pane_current_command == claude` 인 pane 을 전 세션에서 스캔한다.
- 각 pane 의 target(`session:window.pane`), pid, title, `@agent-role`, `@agent-model`, `@agent-status` 를 수집한다.
- 유휴(idle) 판정: 스피너 문자열 부재 + 입력 프롬프트 박스 존재.

### FR-2: 역할 계획 + 태깅
- plans.md 에서 도출된 필요 역할 수를 가용 유휴 pane 에 매핑한다.
- `tmux set-option -p @agent-role/@agent-model/@agent-status` 로 pane 에 각인한다.
- 태깅 후 read-back(`#{@agent-role}`)으로 검증한다.

### FR-3: capacity 진단 + 제안 (human gate)
- 유휴 claude pane 수 N 과 필요 역할 수를 비교한다.
- 충분 시: target→role 배정안을 제안한다.
- 부족 시: 부족분 개수와 배정 예정 목록을 제시하고 사용자에게 추가 실행을 요청한다.
- 사용자 "진행" 지시 전까지 dispatch 하지 않는다.

### FR-4: pane 준비 (기본 수동 / 옵션 자동)
- **기본**: 부족분 pane 은 사용자가 직접 실행한다(취향 영역).
- **옵션**: 사용자 허용 시 `tmux split-window 'claude --model <m>'` 로 부족분을 자동 생성한다.
- "진행" 지시 시 재-discover 하여 새 유휴 pane 을 흡수한다.

### FR-5: dispatch + 완료 감지 (마커 컨벤션)
- dispatch 전 `ready` 확인(스피너 부재).
- 멀티라인 프롬프트는 `load-buffer`+`paste-buffer`+Enter 로 원자적 주입.
- 워커 브리핑에 "완료 시 `[<ROLE>-<N> DONE]`, 차단 시 `[<ROLE>-<N> BLOCKED: 사유]` 출력" 지시.
- `capture-pane` 폴링으로 마커를 감지하고 결과를 수집한다.

### FR-6: 워커 프로파일 지정
- 워커별로 다음 옵션을 설정 가능하게 한다: `model`, `effort`(low/medium/high/max),
  `permission-mode`, `max-budget-usd`, `fast`(opus 런타임 토글), `directives`(행동 지침 텍스트).
- **spawn 경로**: `claude --model --effort --permission-mode --max-budget-usd` launch flag 로 완전 강제.
- **기존 pane**: `/model`·`/fast` 주입 + 브리핑 directive 로 부분 적용(effort/permission/budget 은 런치 시 고정).

### FR-7: attitude 프리셋 + 대상별 선택 기준
- 옵션 묶음을 명명된 프리셋으로 제공: **절약(economy) / 속도(speed) / 품질(quality) / 서술(prose)** (+ custom).
- **orchestrator 전용 모델 = `claude-fable-5` 고정**(다중 에이전트 조율 SOTA, claude-api 레퍼런스). 워커 프리셋은 opus/sonnet/haiku 사용, prose=sonnet.
- 각 프리셋은 model·effort·permission·budget·검증강도·directive 로 확장된다(specs TS-4).
- **구현 대상 성격 → 프리셋 선택 기준**(결정 축·매핑 표)을 제공해 오케스트레이터가 서브태스크별로 자동 선택한다(specs TS-5).
- 사용자는 프리셋/모델을 명시해 override 할 수 있다. 비용·지연 제약 시 한 단계 강등한다.
- 역할별 기본 프리셋 매핑 가능하나, **서브태스크 성격이 역할 기본값보다 우선**한다.

### FR-8: 결과 통합 + 보고
- 수집 결과를 통합하고, reviewer 역할에 교차 검토를 dispatch 한 뒤 사용자에게 보고한다.

## Non-Functional Requirements

- **NFR-1 (안전성)**: 사용자 승인 없이 어떤 pane 에도 send-keys 하지 않는다. 오케스트레이터 자신·미태깅 pane 보호.
- **NFR-2 (결정성)**: 모든 tmux 조작은 `tmuxctl.sh` 서브커맨드로 캡슐화해 재현 가능하게 한다.
- **NFR-3 (관측성)**: 상태는 pane user-option 에 저장되어 `discover` 로 언제든 조회 가능.
- **NFR-4 (견고성)**: idle/완료 판정은 휴리스틱이므로 timeout·재시도·BLOCKED 경로를 가진다.
- **NFR-5 (repo 컨벤션)**: 문서는 한국어, kebab-case 명명, plugin.json+README 필수.

## Constraints

- claude pane 은 API 가 아닌 대화형 TUI → 구조화된 완료 이벤트 없음(마커+휴리스틱으로 대응).
- tmux 만으로 pane 의 현재 모델을 역감지 불가 → `@agent-model` 은 배정 의도, `/model` 주입으로 일치.
- 로컬 tmux 서버 한정(단일 호스트).
- tmux 3.x 이상(`set-option -p` pane user-option 지원) 필요.

## Out of Scope

- claude 내장 team/subagent 기능 활용.
- codex/aider 등 non-claude 에이전트 지원 (후속 과제 — 마커 순응성·idle 휴리스틱 재검증 필요).
- 원격(다른 호스트) tmux 세션 오케스트레이션.
- 워커 간 직접 통신(P2P) — 모든 조정은 오케스트레이터 경유(star topology).

## References

- 실측 근거: 이 환경 tmux 3.7b 에서 discover/capture-pane/send-keys/set-option -p 검증 완료.
- 기존 패턴: `plugins/local-memory`(references+결정적 명령), `plugins/orchwang-general`(scripts/).
