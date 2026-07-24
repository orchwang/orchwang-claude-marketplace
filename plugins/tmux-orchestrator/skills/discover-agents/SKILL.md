---
name: discover-agents
description: 실행 중인 tmux claude pane 을 스캔해 역할·프로파일·유휴 상태와 함께 목록화한다. Use when the user wants to see running claude agents, orchestration candidates, or mentions "에이전트 목록", "pane 확인", "discover agents", "/panes".
---

# discover-agents

전 tmux 세션에서 `claude` 가 실행 중인 pane 을 발견해 오케스트레이션 후보를 목록화하는 skill.

> 모든 tmux 조작은 `scripts/tmuxctl.sh` 를 통해서만 수행한다. tmux 플래그를 직접 다루지 않는다.

## Input

- `/panes` — 인자 없이 실행. 현재 claude pane 맵을 출력한다.

## Process

### Step 1: pane 스캔

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh discover --json
```

- 반환: `[{target, pid, role, model, attitude, status, task, title}, ...]`
- `pane_current_command == claude` 인 pane 만 포함된다.
- `role` 이 빈 문자열이면 **미배정** pane(오케스트레이션에 아직 편입되지 않음)이다.

### Step 2: 유휴 판정

각 pane 에 대해 `status` 가 비어 있거나 `idle` 이면 유휴 후보로 본다.
`status` 가 `busy`/`assigned` 이면 현재 작업 중이므로 새 dispatch 대상에서 제외한다.
필요 시 실시간 확인:

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh ready <target>   # exit 0 = 유휴
```

### Step 3: 맵 출력

사용자에게 아래 형식으로 정리해 보고한다:

```
현재 claude 에이전트 맵 (N개)
  [배정됨]
    synapse:1.2  implementer / sonnet / speed / busy   — "PR까지 풀사이클"
    synapse:1.3  reviewer    / opus   / quality / idle
  [미배정 · 유휴]
    dotfiles:1.2  (idle)  → 오케스트레이션 편입 가능
```

- 오케스트레이터 자기 자신(현재 세션 pane)은 `tech-lead` 로 식별하되 dispatch 대상에서 제외한다.
- `@agent-managed` 표식이 있는 pane 은 오케스트레이터가 spawn 한 것으로 별도 표기한다.

## Output

- claude pane 목록(배정/미배정·유휴/busy 구분).
- read-only. 이 skill 은 어떤 pane 에도 send 하지 않는다(NFR-1).
