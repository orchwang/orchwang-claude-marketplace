# Plans: tmux-orchestrator 플러그인

> 상태: **SDD 진행 / 구현 보류** (2026-07-24)
> 이 문서는 구현 계획서다. 실제 구현은 사용자의 "구현 시작" 지시 후 진행한다.

## Overview

`plugins/tmux-orchestrator/` 를 스캐폴딩하고, 결정적 CLI(`tmuxctl.sh`) → 스킬 → 에이전트 →
커맨드 순으로 상향 구축한다. MVP(discover→dispatch)를 먼저 실동작 검증한 뒤 전체 루프로 확장한다.

## Prerequisites

- tmux ≥ 3.x, claude CLI 설치(로컬).
- 검증용 격리 세션 사용(실작업 pane 미접촉).
- `.claude-plugin/marketplace.json` 쓰기 권한.

## Implementation Steps

### Step 1: 플러그인 스캐폴딩
- `plugins/tmux-orchestrator/{plugin.json, README.md}` 생성.
- `skills/ agents/ commands/ scripts/` 디렉토리 골격.
- plugin.json: name/version(0.1.0)/description/author/license/keywords.

### Step 2: scripts/tmuxctl.sh (핵심 — 결정적 CLI)
- 서브커맨드 구현: `discover, tag, read, ready, send, wait, apply-profile, spawn` (specs TS-2).
- 프리셋 테이블(TS-4) 을 스크립트 상단 맵으로 정의(economy/speed/quality/prose, 모델 opus/sonnet/haiku/fable), `<preset|opts>` 파서.
- `spawn` 은 프리셋을 `--model/--effort/--permission-mode/--max-budget-usd` 로 전개.
- `apply-profile` 은 기존 pane 에 model+fast+directive 만 적용, effort/permission 불일치 시 경고 출력.
- `discover --json` 은 스킬이 파싱하기 쉬운 형식으로(프로파일 필드 포함).
- `ready`/`wait` 판정 정규식은 상단 변수로 분리(TUI 버전 튜닝 용이).
- **격리 세션으로 각 서브커맨드 단위 검증** (특히 send 원자성, wait 마커 감지, spawn flag 전개).

### Step 3: discover-agents skill
- `tmuxctl discover` 호출 → claude pane 목록·유휴 판정 결과를 정리해 반환.
- `/panes` 커맨드가 이 스킬을 사용.

### Step 4: plan-roles skill (게이트)
- plans.md 필요역할 수 입력 → discover 결과와 매칭 → 제안 리포트 생성.
- **서브태스크 성격 → 프리셋 자동 선택**(TS-5 결정 축) 후 배정안에 프리셋 명시.
- 부족 시 부족분·배정예정(프리셋 포함) 목록 제시, "진행" 지시 전 dispatch 금지 명문화.
- spawn 자동생성은 사용자 명시 허용 시에만.

### Step 5: dispatch-task skill
- tag → apply-profile(프리셋/옵션→`/model`·`/fast`·directive) → 브리핑 주입 → ready → send → wait → read 수집.
- BLOCKED/ASK/timeout 에러 경로(specs Error Handling) 구현.
- 역할별 기본 프리셋 매핑 적용, 사용자 override 반영.

### Step 6: orchestrator agent + commands
- `agents/orchestrator/AGENT.md`: 3-Phase 루프 플레이북(Phase A SDD → B 제안게이트 → C 실행).
- `commands/orchestrate.md`, `commands/panes.md` 프론트매터+워크플로우.

### Step 7: 마켓플레이스 등록 + README
- `.claude-plugin/marketplace.json` 에 tmux-orchestrator 항목 추가.
- README(한국어): overview/installation/commands/skills/agents/quick start/license.
- 루트 README·CHANGELOG 갱신.

## Task Breakdown

| # | 산출물 | 의존 |
|---|--------|------|
| 1 | 스캐폴딩 | — |
| 2 | tmuxctl.sh (MVP 핵심) | 1 |
| 3 | discover-agents | 2 |
| 4 | plan-roles | 2,3 |
| 5 | dispatch-task | 2,3 |
| 6 | orchestrator agent + commands | 3,4,5 |
| 7 | 마켓플레이스·README·CHANGELOG | 6 |

## File Change Summary

- 신규: `plugins/tmux-orchestrator/**` (plugin.json, README, scripts/tmuxctl.sh, skills×3, agents×1, commands×2).
- 수정: `.claude-plugin/marketplace.json`, 루트 `README.md`, `CHANGELOG.md`.

## Dependencies Between Steps

```
1 → 2 → {3, 5}
        3 → 4
    {3,4,5} → 6 → 7
```

## Testing Strategy

### Manual Verification (격리 세션)
1. `tmux new-session -d -s orch-test` + 유휴 claude pane 2~3개.
2. `tmuxctl discover` → pane 정확 탐지·유휴 판정 확인.
3. `tmuxctl tag` → `discover` read-back 일치 확인.
4. `tmuxctl setmodel` → 워커 `/model` 반영 확인.
5. `tmuxctl send` → 멀티라인 프롬프트 원자적 주입(조기 submit 없음) 확인.
6. `tmuxctl wait` → 워커가 `[ROLE-N DONE]` 출력 시 감지, timeout 시 exit 1 확인.
7. 전체 `/orchestrate` 소규모 작업으로 A→B→C 게이트 흐름 확인.
8. **정리**: `@agent-managed=1` pane kill, 격리 세션 kill.

### MVP 우선 검증 대상 (리스크 선차단)
- send 원자성(Step 2·5)·wait 마커 감지(Step 2·5) — 가장 깨지기 쉬운 부분 먼저.

## Rollback Plan

- 플러그인은 신규 디렉토리 격리 → 문제 시 `plugins/tmux-orchestrator/` 제거 + marketplace.json 항목 원복.
- spawn 한 pane 은 `@agent-managed=1` 로 식별해 일괄 kill.

## Risk Assessment

| 리스크 | 영향 | 완화 |
|--------|------|------|
| idle/완료 판정 휴리스틱 취약 | 오배정·무한대기 | 정규식 완충 + timeout + 마커 이중화 |
| 멀티라인 조기 submit | dispatch 손상 | load-buffer+paste-buffer 원자화, Step2 우선 검증 |
| 사용자 수동개입 충돌 | 상태 불일치 | 미태깅 pane 제외, dispatch 전 ready 재확인(OQ-4) |
| TUI 버전 변동 | 판정 실패 | 정규식 변수화, claude 단일종만 지원(범위 축소) |

## Progress Tracking

- [ ] Step 1 스캐폴딩
- [ ] Step 2 tmuxctl.sh
- [ ] Step 3 discover-agents
- [ ] Step 4 plan-roles
- [ ] Step 5 dispatch-task
- [ ] Step 6 orchestrator agent + commands
- [ ] Step 7 마켓플레이스·README

## Acceptance Criteria Checklist

- [ ] `/panes` 가 실행 중 claude pane 을 역할·상태와 함께 출력한다.
- [ ] `/orchestrate` 가 SDD → 제안 → (게이트) → 실행 흐름을 따른다.
- [ ] 사용자 승인 전 어떤 워커에도 dispatch 하지 않는다(NFR-1).
- [ ] 부족분 pane 을 사용자가 띄운 뒤 "진행" 시 재-discover 로 흡수한다.
- [ ] spawn 자동생성은 명시 허용 시에만 동작한다.
- [ ] 워커별 model 혼합 활용이 실제 반영된다(spawn flag / `/model` 주입).
- [ ] attitude 프리셋(절약/속도/품질/서술)이 model(opus/sonnet/haiku/fable)·effort·permission·budget·directive 로 전개된다.
- [ ] 구현 대상 성격→프리셋 선택 기준(TS-5)이 배정안에 반영된다.
- [ ] spawn 워커는 프로파일이 launch flag 로 완전 강제되고, 기존 pane 불일치는 경고된다.
- [ ] 완료 마커 감지·수집·통합 보고가 동작한다.
- [ ] README·marketplace.json·CHANGELOG 갱신 완료.
