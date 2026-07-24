---
name: plan-roles
description: SDD 계획의 필요 역할 수와 현재 유휴 claude pane 을 대조해 배정안·프리셋을 제안하고, 부족분 추가 실행을 요청한다(human gate). Use when orchestrating and mentions "역할 배정", "capacity 진단", "plan roles", "오케스트레이션 제안".
---

# plan-roles

작업 계획에서 도출된 필요 역할과 가용 claude pane 을 매칭해 **제안 리포트**를 만들고,
사용자 승인(게이트) 전까지 어떤 dispatch 도 하지 않는 skill. 오케스트레이션의 Phase B 를 담당한다.

> 프리셋·선택 기준은 `references/presets.md` 를 참조한다.
> tmux 조작은 `scripts/tmuxctl.sh` 로만 수행한다.

## Input

- 상위 오케스트레이터(orchestrator 에이전트)가 SDD 산출물(plans.md)에서 도출한 **필요 역할·서브태스크 목록**.
- 없으면 먼저 `/orchestrate` 로 Phase A(SDD)를 완료하도록 안내한다.

## Process

### Step 1: 필요 역할·프리셋 산정

각 서브태스크의 성격을 `references/presets.md` 의 **선택 기준(결정 축)** 으로 평가해 프리셋을 정한다.

- 서술(문서/네이밍) → prose / 비가역·고위험 → quality / 모호 → quality(선계획)
- 교차검토 → quality / 대량·기계적 → economy / 그 외 일반 구현 → speed(기본)
- 서브태스크 성격이 역할 기본값보다 우선한다.

산출: `[{subtask, role, preset}, ...]` 와 필요 역할 수 집계.

### Step 2: capacity 진단

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh discover --json
```

- 유휴·미배정 claude pane 수 N 을 센다(오케스트레이터 자신 제외).
- 필요 역할 수와 비교한다.

### Step 3: 제안 리포트 생성 (게이트)

아래 형식으로 사용자에게 제안한다. **여기서 멈추고 승인을 기다린다.**

```
[SDD] plans.md 기준 필요 역할: implementer ×2(speed), reviewer ×1(quality)

[현재 세션 진단] 유휴 claude pane: 2개
  배정 예정:
    synapse:1.2 → implementer-1 / speed(sonnet)
    synapse:1.3 → reviewer-1    / quality(opus)
  부족: implementer 1개 → claude pane 1개 추가 실행 필요

[기존 pane 프로파일 경고]
  synapse:1.2 는 런치 시 effort 가 고정되어 speed 프리셋의 effort=medium 을 강제할 수 없음(경고).

▶ 다음 중 하나를 지시해 주세요:
  1) pane 1개를 직접 띄운 뒤 "진행"
  2) "자동 생성 허용" — 제가 speed 프리셋으로 pane 을 spawn
```

- 부족분 pane 준비는 **사용자 수동이 기본**(취향 영역). 자동 생성은 사용자가 명시 허용할 때만.
- 승인 전 `tag`/`send`/`spawn` 을 실행하지 않는다.

### Step 4: 승인 후 흡수

사용자가 "진행" 하면:

- 재-`discover` 로 새로 뜬 유휴 pane 을 흡수한다.
- "자동 생성 허용" 이면:
  ```
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh spawn <session> <count> <preset>
  ```
- 최종 배정안(target→role/preset)을 확정해 `dispatch-task` 로 넘긴다.

## Output

- 제안 리포트(배정안 + 부족분 + 프로파일 경고).
- 승인 후: 확정 배정안. 승인 전에는 상태 변경 없음.
