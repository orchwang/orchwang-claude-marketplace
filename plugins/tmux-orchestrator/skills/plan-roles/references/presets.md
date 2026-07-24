# attitude 프리셋 & 선택 기준 (reference)

## 모델 라인업 (claude-api 레퍼런스 확정)

| model | 티어·성격 | 적합 |
|-------|-----------|------|
| `fable` | **최상위** — 장기 에이전틱·다중 에이전트 조율 SOTA | **orchestrator 전용**(워커 배정 금지) |
| `opus` | Opus 티어 최상위 — 고자율·복잡 추론 | 복잡·고위험 로직, 리뷰, 아키텍처 |
| `sonnet` | 속도/품질/비용 균형 | 일반 기능 구현 주력, 서술 |
| `haiku` | 최속·최저비용 | 대량·단순·기계적 작업 |

> Fable 은 "reliably sustains ongoing communications with long-running sub-agents and peer agents"
> (비동기 다중 에이전트 조율)에 명시적 SOTA → orchestrator 두뇌로 고정. Opus 4.8 은 위임에 소극적이라 열위.

## 프리셋

| 프리셋 | model | effort | permission | budget | 검증 | directive(브리핑 삽입) |
|--------|-------|--------|-----------|--------|------|----------------------|
| economy(절약) | haiku | low | manual | 낮게 캡 | 최소 | "최소 토큰. 탐색·부연 금지. 확인질문 자제. 결론 우선." |
| speed(속도) | sonnet | medium | acceptEdits | 중간 | 경량 | "신속 처리. 병렬 우선. 무거운 검증 생략. 막히면 즉시 ASK." |
| quality(품질) | opus | high | acceptEdits | 무제한 | 철저 | "엣지케이스·실패모드 검토. 근거 제시. 스스로 반증." |
| prose(서술) | sonnet | medium | acceptEdits | 중간 | 문체·정합성 | "명료·일관된 서술. 독자 관점. 코드 대신 문서·표현에 집중." |

> **orchestrator(tech-lead) 세션 자체는 `claude-fable-5` 로 실행**한다. 위 프리셋은 **워커**에만 적용되며 fable 은 포함하지 않는다.

## 선택 기준 — 결정 축 (위에서 걸리면 확정)

1. 산출물이 **서술**인가(문서/네이밍/릴리즈노트/PR 본문)? → **prose**
2. **비가역·고위험**인가(마이그레이션·동시성·인증/결제·스키마·아키텍처)? → **quality**
3. 요구가 **모호·미확정**인가? → **quality** (선계획 후 재평가)
4. **교차검토·감사**인가(code/security review)? → **quality**
5. **대량·반복·기계적**이며 저위험인가? → **economy**
6. 그 외 일반 기능 구현(명확·중위험) → **speed** (기본값)

## 구현 대상 성격별 매핑

| 성격 | 예시 | 프리셋 |
|------|------|--------|
| 대량·반복·기계적, 저위험 | 일괄 rename, boilerplate, import 정리 | economy |
| 일반 기능 구현, 명확·중위험 | CRUD, 엔드포인트, 표준 컴포넌트 | speed |
| 복잡·미묘 / 고위험 / 비가역 | 동시성, DB 마이그레이션, 인증·결제, 아키텍처 | quality |
| 교차검토·감사 | code review, security review | quality |
| 요구 모호·탐색 | 미확정 spec, 설계 대안 도출 | quality(선계획) |
| 문서·서술·네이밍 | README, ADR, API doc, 릴리즈노트, PR 본문 | prose |
| 발산·다양성 필요 | 대안 다수 생성, 리뷰 다관점 | prose + 다중 프리셋 패널 |

## 적용 원칙

- **서브태스크 성격 > 역할 기본값**. reviewer 라도 대상이 문서면 prose 고려.
- 역할 기본값(override 가능): tech-lead→quality, implementer→speed, reviewer→quality, 대량단순→economy, 문서→prose.
- 사용자 명시 프리셋/모델이 자동선택을 override.
- 비용·지연 제약이 강하면 한 단계 강등(quality→speed→economy)하고 근거를 리포트에 남긴다.

## 강제 지점 (중요)

| 옵션 | spawn(신규) | 기존 pane |
|------|-------------|----------|
| model | `--model` flag | `/model` 주입 |
| effort | `--effort` flag | ⚠️ 런타임 변경 불가 → 경고 |
| permission | `--permission-mode` flag | ⚠️ 고정 |
| budget | `--max-budget-usd` flag | ⚠️ 고정 |
| fast | — | `/fast` 주입(opus) |
| directive | 브리핑 텍스트 | 브리핑 텍스트 |

→ 완전한 프로파일 강제는 **spawn 경로에서만** 보장. 기존 pane 은 model+fast+directive 만 적용하고 나머지는 경고.
