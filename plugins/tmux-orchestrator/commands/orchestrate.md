---
name: orchestrate
description: tmux claude pane 들을 오케스트레이션한다. SDD 계획 → capacity 진단·제안(승인 게이트) → 프로파일 기반 dispatch → 완료감지 → 결과 통합.
---

# orchestrate

현재 세션을 tech-lead 로 삼아 실행 중인 다른 claude pane 들에 역할을 배정하고 작업을 지휘하는 command.

## Input

- `/orchestrate <작업 설명>` — 작업을 지시하며 오케스트레이션 시작.
- `/orchestrate` — 인자 없이 실행하면 어떤 작업을 오케스트레이션할지 물어본다.

## Process

`orchestrator` 에이전트를 구동해 3-Phase 루프를 수행한다.

### Phase A — 계획 (SDD)
1. 작업을 분석해 requirements/specs/plans(또는 경량 계획)를 작성하고 **필요 역할·서브태스크**를 도출한다.
2. 서브태스크 성격 → 프리셋(economy/speed/quality/prose)을 예비 선정한다.

### Phase B — 진단·제안 (게이트)
3. `discover-agents` 로 유휴 claude pane 을 집계한다.
4. `plan-roles` 로 배정안·부족분·프로파일 경고 리포트를 출력하고 **멈춘다**.
5. 사용자가 pane 준비 후 "진행"(또는 "자동 생성 허용")을 지시할 때까지 대기한다.

### Phase C — 실행
6. 재-`discover` 로 새 유휴 pane 흡수 → `dispatch-task` 로 프로파일 적용·브리핑·dispatch.
7. `wait` 로 완료 마커 감시(DONE/BLOCKED/timeout) → 결과 수집 → reviewer 교차검토.
8. 통합 결과 보고 + spawn pane 정리 확인.

## 제약

- 사용자 승인 전 어떤 pane 에도 send/tag/spawn 하지 않는다.
- 오케스트레이터 자신·미태깅 pane 은 dispatch 대상 제외.
- 대상은 claude pane 만. timeout/BLOCKED 는 자동 재시도 없이 에스컬레이션.

## Output

- Phase 별 진행 상황과 최종 통합 보고.
