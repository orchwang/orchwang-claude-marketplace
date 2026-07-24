---
name: dispatch-task
description: 확정된 배정안대로 워커 claude pane 에 프로파일을 적용하고 서브태스크를 dispatch 한 뒤 마커로 완료를 감지·수집한다. Use when orchestration is approved and mentions "작업 배정", "dispatch", "워커 실행", "진행".
---

# dispatch-task

승인된 배정안을 받아 각 워커 pane 에 프로파일을 적용하고 서브태스크를 주입·감시·수집하는 skill.
오케스트레이션의 Phase C 를 담당한다.

> tmux 조작은 `scripts/tmuxctl.sh` 로만 수행한다.
> **전제**: `plan-roles` 의 사용자 게이트를 통과한 확정 배정안이 있어야 한다. 승인 없이 호출 금지(NFR-1).

## Input

- 확정 배정안: `[{target, role, preset, subtask}, ...]`.

## Process

각 워커에 대해 아래를 수행한다(여러 워커는 순차 태깅 후 병렬 감시 가능).

### Step 1: 프로파일 적용

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh apply-profile <target> <preset>
```

- `@agent-role/@agent-model/@agent-attitude` 태깅 + `/model` 주입.
- spawn 으로 생성된 pane 은 이미 flag 로 프로파일이 강제되어 있으므로 model 재주입만 확인.
- 기존 pane 의 effort/permission 경고가 나오면 사용자에게 이미 고지된 사항이므로 진행한다.
- 상태 태깅: `tmuxctl tag <target> role=<role> task=<slug> status=assigned`.

### Step 2: 브리핑 + 서브태스크 주입

브리핑 프롬프트 파일을 작성한다(마커 프로토콜 포함):

```
[역할: <ROLE>-<N> / 모델: <MODEL> / 프리셋: <PRESET>]
목표: <subtask 요약>
컨텍스트: <파일·제약·수용기준>
<프리셋 directive — references/presets.md 참조>

완료 시 반드시 마지막 줄에 `[<ROLE>-<N> DONE]` 을 출력하라.
차단 시 `[<ROLE>-<N> BLOCKED: <사유>]` 를 출력하라.
질문이 필요하면 `[<ROLE>-<N> ASK: <질문>]` 을 출력하고 대기하라.
```

주입 전 유휴 확인 → 원자적 주입:

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh ready <target>          # exit 0 아니면 대기 후 재확인
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh send  <target> <prompt-file>
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh tag   <target> status=busy
```

### Step 3: 완료 감시

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh wait <target> <ROLE>-<N> <timeout>
```

- exit 0 = DONE → `tag status=done` 후 결과 수집.
- exit 2 = BLOCKED → `tag status=blocked`, `read` 로 사유 수집해 사용자에게 에스컬레이션.
- exit 1 = timeout → `read` 로 현재 상태 캡처해 보고. **자동 재dispatch 하지 않는다.**

### Step 4: 결과 수집 + 통합

```
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tmuxctl.sh read <target> 200
```

- 각 워커 결과를 수집한다.
- reviewer 역할이 있으면 implementer 산출물을 reviewer 에 교차검토 dispatch(Step 1~3 반복).
- 통합 결과를 사용자에게 보고한다.

## Error Handling

| 상황 | 처리 |
|------|------|
| ready 실패(busy) | 대기 후 재확인, N회 초과 시 사용자 보고 |
| timeout | read 캡처 보고, 자동 재시도 금지 |
| BLOCKED/ASK | status=blocked, 사유 수집·에스컬레이션 |
| pane 소멸 | 다음 discover 에서 감지 → 배정 취소·재계획 |
| 미태깅 pane | 대상에서 제외 |

## Output

- 워커별 결과 수집·통합 보고.
- spawn 된(`@agent-managed`) pane 은 작업 종료 후 정리 여부를 사용자에게 확인한다.
