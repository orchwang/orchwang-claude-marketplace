# tmux-orchestrator

실행 중인 tmux `claude` pane 들을 발견해 역할을 배정하고, 하나의 오케스트레이터 세션(tech-lead)이
멀티 에이전트 협업을 지휘하는 Claude Code 플러그인.

> ⚠️ **실험적(v0.1.0)** — claude TUI 를 대화형으로 구동하는 특성상 완료 감지·유휴 판정은 휴리스틱(마커 컨벤션 + 화면 폴링)입니다.

## Overview

- **Discover**: 전 tmux 세션에서 `claude` pane 을 스캔(역할·프로파일·상태 포함).
- **Role & Profile**: pane user-option(`@agent-*`)에 역할·모델·attitude 프리셋을 각인.
- **Human gate**: SDD 계획 → capacity 진단 → **제안 후 사용자 승인** 전까지 무동작.
- **Dispatch**: 프로파일 적용 + 브리핑 주입 + 마커(`[ROLE-N DONE]`)로 완료 감지·수집.
- **Attitude 프리셋**: 구현 대상 성격에 따라 economy / speed / quality / prose 자동 선택.

상태는 tmux pane user-option 에만 저장되어 외부 파일이 없고 pane 소멸 시 자동 정리됩니다.

## Installation

```
/plugin install tmux-orchestrator@orchwang-marketplace
```

**요구사항**: tmux ≥ 3.x(`set-option -p` pane user-option 지원), claude CLI(`--model/--effort/--permission-mode/--max-budget-usd` 지원).

## Commands

| 커맨드 | 설명 |
|--------|------|
| `/orchestrate <작업>` | SDD → 진단·제안(게이트) → dispatch → 통합의 3-Phase 오케스트레이션 시작 |
| `/panes` | 실행 중인 claude pane 맵 출력(read-only) |

## Skills

| 스킬 | 설명 |
|------|------|
| `discover-agents` | claude pane 스캔·유휴 판정·맵 출력 |
| `plan-roles` | 필요 역할↔가용 pane 매칭, 프리셋 선택, 제안 리포트(게이트) |
| `dispatch-task` | 프로파일 적용·브리핑 주입·dispatch·마커 완료감지·수집 |

## Agents

| 에이전트 | 설명 |
|----------|------|
| `orchestrator` | tech-lead 로서 3-Phase 루프를 구동. 승인 게이트·자기보호·자동재시도 금지 원칙 준수 |

## 프로파일 & attitude 프리셋

| 프리셋 | model | effort | 적합 대상 |
|--------|-------|--------|-----------|
| economy(절약) | haiku | low | 대량·반복·기계적, 저위험 |
| speed(속도) | sonnet | medium | 일반 기능 구현(기본값) |
| quality(품질) | opus | high | 복잡·고위험·비가역, 리뷰 |
| prose(서술) | sonnet | medium | 문서·네이밍·릴리즈노트 |

> **orchestrator(tech-lead) 세션 전용 모델 = `claude-fable-5`.** Fable 5 는 장기 에이전틱·비동기 다중 에이전트 조율에 SOTA(claude-api 레퍼런스)라 지휘 두뇌로 고정. orchestrator 세션은 `claude --model fable` 로 실행하기를 권장. 위 프리셋은 워커에만 적용됩니다.

- **완전 강제는 spawn 경로에서만** (`claude --model --effort --permission-mode --max-budget-usd`).
- 기존 사용자 pane 은 `/model`·`/fast`·브리핑 directive 만 적용, effort/permission 불일치는 경고.

## Quick Start

```
# 1) 워커로 쓸 claude pane 을 몇 개 띄워둔다(빈 상태)
# 2) 오케스트레이터 세션에서:
/panes                      # 현재 claude 에이전트 맵 확인
/orchestrate 사용자 인증 리팩토링   # SDD → 제안 리포트까지 진행 후 멈춤
# 3) 제안을 보고 부족분 pane 을 띄운 뒤:
진행                        # 재-discover → dispatch → 완료감지 → 통합 보고
```

## 내부 도구

- `scripts/tmuxctl.sh` — 모든 tmux 조작을 캡슐화한 결정적 CLI
  (`discover/tag/read/ready/send/wait/apply-profile/spawn/preset`).
  스킬/에이전트는 tmux 플래그를 직접 다루지 않고 이 CLI 만 호출합니다.

## 제약 / 범위

- 1차 범위는 **claude pane 만**. codex/aider 등은 후속 과제.
- 로컬 단일 tmux 서버 한정. 워커 간 직접 통신 없음(star topology).
- 완료/유휴 판정은 휴리스틱 — TUI 버전 변동 시 `tmuxctl.sh` 상단 정규식 조정.

## License

MIT
