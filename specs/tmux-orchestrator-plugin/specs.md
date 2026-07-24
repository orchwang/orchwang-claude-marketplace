# Specs: tmux-orchestrator 플러그인

> 상태: **SDD 진행 / 구현 보류** (2026-07-24)

## Overview

tmux CLI 를 Claude Code 의 Bash 로 호출해 멀티 claude pane 을 오케스트레이션한다.
상태는 tmux pane user-option 에 저장하고, 완료는 마커 컨벤션으로 감지한다.
모든 tmux 조작은 `scripts/tmuxctl.sh` 로 캡슐화하고, 스킬/에이전트는 이 결정적 CLI 만 호출한다.

## 디렉토리 구조

```
plugins/tmux-orchestrator/
├── plugin.json
├── README.md
├── scripts/
│   └── tmuxctl.sh          # discover/read/ready/tag/send/wait/spawn 캡슐화
├── skills/
│   ├── discover-agents/    # SKILL.md — claude pane 스캔·유휴 판정
│   ├── plan-roles/         # SKILL.md — 필요역할 산정·capacity 진단·제안(게이트)
│   └── dispatch-task/      # SKILL.md — 태깅·주입·dispatch·마커 폴링·수집
├── agents/
│   └── orchestrator/       # AGENT.md — 3-Phase 루프 구동(tech-lead)
└── commands/
    ├── orchestrate.md      # /orchestrate — 오케스트레이션 세션 시작
    └── panes.md            # /panes — 현재 에이전트 맵 출력(read-only)
```

## Technical Specifications

### TS-1: 상태 스키마 (pane user-options)

| 옵션 | 값 예시 | 의미 |
|------|---------|------|
| `@agent-role` | `tech-lead` `implementer` `reviewer` | 배정된 역할 |
| `@agent-model` | `opus` `sonnet` `haiku` | 배정 의도 모델 |
| `@agent-attitude` | `economy` `quality` `speed` `custom` | 적용된 프리셋 |
| `@agent-effort` | `low` `medium` `high` `max` | reasoning effort |
| `@agent-permission` | `manual` `acceptEdits` `plan` `bypassPermissions` | 권한 모드 |
| `@agent-budget` | `2.0` | max-budget-usd (선택) |
| `@agent-status` | `idle` `assigned` `busy` `done` `blocked` | 워크플로우 상태 |
| `@agent-task` | `implement-tmuxctl` | 현재 서브태스크 슬러그 |
| `@agent-managed` | `1` | 오케스트레이터가 spawn 한 pane 표식(정리용) |

- 미태깅 pane 은 `@agent-role` 빈 문자열 → 오케스트레이터가 절대 dispatch 하지 않음(NFR-1).

### TS-2: tmuxctl.sh 서브커맨드

| 커맨드 | 동작 | 구현 근간 |
|--------|------|-----------|
| `discover [--json]` | claude pane 목록(target/pid/title/role/model/status) | `list-panes -a -F` + user-option 필드 |
| `tag <target> role=<r> [model=<m>] [status=<s>]` | pane 에 역할·모델·상태 각인 | `set-option -p -t <target> @agent-*` |
| `read <target> [lines]` | pane 화면/스크롤백 출력 | `capture-pane -p -t <target> [-S -<lines>]` |
| `ready <target>` | 스피너 부재 & 프롬프트 박스 존재 시 exit 0 | `capture-pane` 정규식 판정 |
| `send <target> <file>` | 파일 내용 원자적 주입 후 제출 | `load-buffer <file>` → `paste-buffer -t` → `send-keys -t Enter` |
| `wait <target> <marker> [timeout=600]` | 마커 출력까지 폴링(exit 0=발견, 1=timeout, 2=blocked) | 루프 `capture-pane` grep `[<marker>]` / `BLOCKED` |
| `apply-profile <target> <preset\|opts>` | 기존 pane 에 프로파일 부분 적용 | `/model`·`/fast` 주입 + tag + 브리핑 directive (effort/permission 은 런타임 변경 불가 → 경고) |
| `spawn <session> <count> <preset\|opts>` | 프로파일대로 claude pane 자동 생성(옵션) | `split-window 'claude --model <m> --effort <e> --permission-mode <p> [--max-budget-usd <b>]'` + tag `@agent-managed=1` |

- 판정 정규식은 claude TUI 버전 변동 대비 완충(스피너 후보: `Cogitated|Thinking|esc to interrupt`).
- `<preset|opts>` 는 프리셋명(`economy`) 또는 개별 옵션(`model=opus effort=high`). 개별 옵션은 프리셋 위에 override.

### TS-4: 워커 프로파일 & attitude 프리셋

프로파일 = 워커에 적용되는 옵션 묶음. 프리셋은 프로파일의 명명된 기본값 세트다.

**모델 라인업 (claude-api 레퍼런스 확정 — fable 5 / opus 4.8 / sonnet 5 / haiku 4.5)**

| model | 티어·성격 (레퍼런스 근거) | 단가($/1M) | 적합 |
|-------|--------------------------|-----------|------|
| `fable` | **최상위** — 가장 유능. 장기 에이전틱·다중 에이전트 조율 SOTA | $10/$50 | **orchestrator(고정)**, 최난도 추론 |
| `opus` | Opus 티어 최상위 — 고자율·복잡 추론 | $5/$25 | 복잡·고위험 로직, 리뷰, 아키텍처 |
| `sonnet` | 속도/품질/비용 균형 | $3/$15 | 일반 기능 구현 주력 |
| `haiku` | 최속·최저비용 | $1/$5 | 대량·단순·기계적 작업 |

> **orchestrator 전용 모델 = `claude-fable-5` 고정.** 레퍼런스상 Fable 이 "parallel sub-agent
> delegation and collaboration — reliably sustains ongoing communications with long-running
> sub-agents and peer agents"(비동기 다중 에이전트 조율)에 명시적 SOTA. Opus 4.8 은 위임에
> 소극적("under-reaches for subagents by default")이라 orchestrator 로는 열위. 비용은 2배지만
> orchestrator 는 세션당 1개이고 워커는 저렴한 티어를 쓰므로 프리미엄이 정당.

**프리셋**

| 프리셋 | model | effort | permission | budget | 검증 강도 | directive(브리핑 삽입) |
|--------|-------|--------|-----------|--------|-----------|----------------------|
| **economy**(절약) | haiku | low | manual | 낮게 캡 | 최소 | "최소 토큰. 탐색·부연 금지. 확인질문 자제. 결론 우선." |
| **speed**(속도) | sonnet | medium | acceptEdits | 중간 | 경량(무거운 검증 생략) | "신속 처리. 병렬 우선. 무거운 검증 생략. 막히면 즉시 ASK." |
| **quality**(품질) | opus | high | acceptEdits | 무제한 | 철저(self-review·엣지케이스) | "엣지케이스·실패모드 검토. 근거 제시. 스스로 반증." |
| **prose**(서술) | sonnet | medium | acceptEdits | 중간 | 문체·정합성 | "명료·일관된 서술. 독자 관점. 코드 변경 대신 문서·표현에 집중." |
| **orchestrator**(조율·전용) | **fable** | high | acceptEdits | 철저 | 다중 에이전트 조율 | (orchestrator 세션 전용. 워커에는 배정하지 않음) |

### TS-5: 프리셋 선택 기준 (구현 대상 성격 → 프리셋)

오케스트레이터는 각 서브태스크의 성격을 아래 **결정 축**으로 평가해 프리셋을 자동 선택한다.

**결정 축 (우선순위 순 — 위에서 걸리면 확정)**

1. **산출물이 코드가 아니라 서술인가?** (문서/네이밍/릴리즈노트/PR 본문) → **prose**
2. **되돌리기 어렵거나 고위험인가?** (마이그레이션·동시성·인증/결제·스키마·아키텍처) → **quality**
3. **요구가 모호·미확정인가?** → **quality** (먼저 SDD/설계, 이후 분해해 재평가)
4. **교차검토·감사인가?** (code/security review) → **quality**
5. **대량·반복·기계적이며 저위험인가?** (일괄 rename·boilerplate·import 정리) → **economy**
6. **그 외 일반 기능 구현 (명확·중위험)** → **speed** (기본값)

**구현 대상 성격별 매핑 표**

| 구현 대상 성격 | 예시 | 권장 프리셋 |
|----------------|------|-------------|
| 대량·반복·기계적, 저위험 | 일괄 rename, boilerplate 생성, import 정리 | economy |
| 일반 기능 구현, 명확·중위험 | CRUD, 엔드포인트, 표준 컴포넌트 | speed |
| 복잡·미묘 로직 / 고위험 / 비가역 | 동시성, DB 마이그레이션, 인증·결제, 아키텍처 | quality |
| 교차검토·감사 | code review, security review | quality |
| 요구 모호·탐색적 | 미확정 spec, 설계 대안 도출 | quality(선계획) → 이후 재평가 |
| 문서·서술·네이밍 | README, ADR, API doc, 릴리즈노트, 커밋/PR 서술 | prose |
| 발산·다양성 필요 | 설계 대안 다수 생성, 리뷰 패널 다관점 | prose + 다중 프리셋 패널 |

**적용 원칙**
- 역할 기본 프리셋(TS-4 하단)보다 **서브태스크 성격이 우선**한다. 예: reviewer 라도 대상이 문서면 prose 고려.
- 사용자가 프리셋/모델을 명시하면 자동 선택을 override 한다.
- 비용·지연 제약이 강하면 한 단계 낮은 프리셋으로 강등(quality→speed, speed→economy)하고 리포트에 근거를 남긴다.

**적용 메커니즘 (옵션별 강제 지점)**

| 옵션 | spawn(신규) | 기존 pane | 근거 |
|------|-------------|----------|------|
| model | `--model` flag | `/model` 주입 | 둘 다 가능 |
| effort | `--effort` flag | ⚠️ 런타임 변경 제한 → 고정, 불일치 시 경고 | CLI flag only |
| permission | `--permission-mode` flag | ⚠️ 고정 | CLI flag only |
| budget | `--max-budget-usd` flag | ⚠️ 고정 | CLI flag only |
| fast | (해당 없음) | `/fast` 주입(opus 한정) | 런타임 토글 |
| directive | 브리핑 텍스트 | 브리핑 텍스트 | 프롬프트 |

- **원칙**: 완전한 프로파일 강제는 `spawn` 경로에서만 보장. 기존 사용자 pane 은 model+fast+directive 만 적용하고,
  effort/permission/budget 불일치는 제안 리포트에 **경고로 표기**한다(강제하지 않음).
- **역할 기본 프리셋(override 가능)**: tech-lead→quality, implementer→speed, reviewer→quality,
  대량 단순작업→economy, 문서·서술 작업→prose. 단 서브태스크 성격이 역할 기본값보다 우선(TS-5).

### TS-3: 워커 브리핑 프로토콜 (dispatch 프롬프트 삽입)

```
[역할: <ROLE>-<N> / 모델: <MODEL>]
목표: <subtask 요약>
컨텍스트: <파일·제약>
완료 시 반드시 마지막 줄에 `[<ROLE>-<N> DONE]` 을 출력하라.
차단 시 `[<ROLE>-<N> BLOCKED: <사유>]` 를 출력하라.
질문이 필요하면 `[<ROLE>-<N> ASK: <질문>]` 을 출력하고 대기하라.
```

## Architecture

- **토폴로지**: star. 오케스트레이터(tech-lead)가 허브, 워커는 스포크. 워커 간 직접 통신 없음.
- **오케스트레이터**: `/orchestrate` 를 실행한 현재 claude 세션. SDD·계획·배정·수집·통합 담당.
- **워커**: `@agent-role` 로 태깅된 다른 claude pane.
- **상태 저장소**: tmux pane user-option (외부 파일 없음, pane 소멸 시 자동 정리).
- **통신 채널**: send(주입) / capture-pane(관측) — 단방향 2채널.

### 3-Phase 워크플로우 (human-gated)

```
Phase A — 계획(SDD)
  1. 사용자 작업 지시
  2. requirements/specs/plans 작성
  3. plans.md → 필요 역할 수 도출

Phase B — 진단·제안(게이트)
  4. discover → 유휴 claude pane 수 N
  5. N vs 필요역할 매칭 → 제안 보고(배정안 / 부족분 M)
  6. [GATE] 사용자가 pane 준비 후 "진행" 지시

Phase C — 실행
  7. 재-discover → 새 유휴 pane 흡수
  8. tag + apply-profile(프리셋→model/effort/…) + 브리핑(directive) 주입
  9. ready 확인 → send(dispatch)
 10. wait(마커 폴링) → read(결과 수집)
 11. reviewer 교차검토 → 통합 → 사용자 보고
```

## API / Interface Design

### Slash Commands
- `/orchestrate [작업 설명]` — Phase A 부터 오케스트레이션 시작.
- `/panes` — 현재 에이전트 맵(target/role/model/status) read-only 출력.

### Agent Trigger
- `agents/orchestrator/AGENT.md` — `/orchestrate` 실행 시 3-Phase 루프를 구동.

### spawn 옵션 게이트
- 제안 단계에서 사용자가 "자동 생성 허용" 을 명시할 때만 `tmuxctl spawn` 실행.
- 제안 리포트는 각 워커의 프리셋/옵션(model·effort·permission·budget)을 함께 제시하고, 기존 pane 의 불일치를 경고한다.

## Error Handling

| 상황 | 처리 |
|------|------|
| dispatch 대상이 busy | `ready` 실패 → 대기 후 재확인, N회 초과 시 사용자 보고 |
| 완료 마커 timeout | `wait` exit 1 → `read` 로 현재 상태 캡처해 사용자에게 보고, 자동 재dispatch 안 함 |
| 워커 BLOCKED/ASK | `@agent-status=blocked` 로 표기, 오케스트레이터가 사유 수집해 사용자에게 에스컬레이션 |
| pane 소멸(사용자 종료) | 다음 discover 에서 누락 감지 → 배정 취소·재계획 |
| 미태깅 pane | dispatch 대상에서 원천 제외(NFR-1) |

## Dependencies

### 외부 의존성
- tmux ≥ 3.x (pane user-option `set-option -p` / `#{@name}` 지원).
- claude CLI (워커 실행). `/model` 슬래시 커맨드 지원.

### 내부 의존성
- 없음(독립 플러그인). 단 마켓플레이스 `.claude-plugin/marketplace.json` 등록 필요.

## Open Questions

- OQ-1: 스피너/프롬프트 판정 정규식의 claude TUI 버전 호환 범위 — 구현 시 실측 필요.
- OQ-2: `wait` 폴링 주기·timeout 기본값 튜닝(현재 안 600s, 주기 2~5s 가정).
- OQ-3: 오케스트레이터가 여러 워커를 동시 dispatch 시 병렬 폴링 방식(순차 vs 라운드로빈).
- OQ-4: dispatch 중 사용자 수동 개입 충돌 방지 락 컨벤션 필요 여부.
- OQ-5: 기존 pane 에서 effort 를 런타임 변경할 슬래시 커맨드 존재 여부 — 없으면 spawn-only 로 확정.
- OQ-6: 프리셋 커스터마이즈 저장 위치(플러그인 기본값 vs 사용자 설정 파일) — 사용자 정의 프리셋 지원 시.
- ~~OQ-7~~ **해소**: Fable 5 는 서술 특화가 아니라 **최상위 추론·다중 에이전트 조율 티어**(claude-api 레퍼런스).
  → orchestrator 전용 모델로 고정. prose 프리셋은 sonnet 으로 정정.
