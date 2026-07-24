---
name: panes
description: 실행 중인 tmux claude pane 을 역할·프로파일·유휴 상태와 함께 목록화한다(read-only).
---

# panes

현재 오케스트레이션 후보인 claude pane 맵을 출력하는 command. 어떤 pane 도 변경하지 않는다.

## Input

- `/panes` — 인자 없이 실행.

## Process

`discover-agents` 스킬을 호출한다.

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh discover
```

- `pane_current_command == claude` 인 pane 만 표기.
- 배정/미배정, 유휴/busy, `@agent-managed`(spawn 된 pane) 구분.

## Output

- claude 에이전트 맵(target / role / model / attitude / status / title).
- read-only. send/tag/spawn 없음.
