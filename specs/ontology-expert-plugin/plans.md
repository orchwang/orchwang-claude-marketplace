# Plans: ontology-expert plugin

> Created: 2026-07-20
> Status: Draft

## 구현 순서

1. **디렉토리 스캐폴딩**
   - `plugins/ontology-expert/{skills/ontology-expert/references,agents/ontology-expert}` 생성

2. **references 3종 작성**
   - `modeling-primitives.md`
   - `mapping-and-actions.md`
   - `foundations-and-comparisons.md`

3. **SKILL.md 작성** — "의미 계층 ≠ 물리 데이터 모델" 원칙 중심, references 인덱싱

4. **AGENT.md 작성** — FDE 설계 워크플로

5. **plugin.json / README.md 작성**

6. **마켓플레이스 등록** (data-engineer와 함께 일괄)
   - `.claude-plugin/marketplace.json`
   - 루트 `README.md`
   - `CHANGELOG.md`
   - 루트 `plugin.json` version bump

7. **검증**
   - JSON 유효성, frontmatter·필수 섹션·kebab-case·시크릿 부재
   - (선택) `/sync-specs ontology-expert-plugin`

## 검증 체크리스트

- [ ] plugin.json 유효 JSON, 메타 정확
- [ ] SKILL/AGENT frontmatter description에 한/영 트리거 존재
- [ ] README 필수 섹션 6종 포함
- [ ] references 3종 존재 및 SKILL에서 링크
- [ ] marketplace.json·루트 README·CHANGELOG 갱신
- [ ] 로컬 절대경로·시크릿 미포함

## 리스크 / 메모

- **원리 vs 벤더**: Palantir Foundry의 온톨로지 개념에서 유래하지만, 특정 제품 종속 서술을 피하고 이식 가능한 원리로 기술.
- **data-engineer와 경계**: 물리 파이프라인/저장/처리는 data-engineer. 온톨로지는 그 위 의미 계층. 상호 참조로 연결.
- **액션 지향 강조**: 온톨로지를 "읽기용 데이터 모델"로 오해하지 않도록 액션/write-back을 1급으로 다룸.
