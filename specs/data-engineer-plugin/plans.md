# Plans: data-engineer plugin

> Created: 2026-07-20
> Status: Draft

## 구현 순서

1. **디렉토리 스캐폴딩**
   - `plugins/data-engineer/{skills/data-engineer/references,agents/data-engineer}` 생성

2. **references 3종 작성** (지식 밀도 우선)
   - `lifecycle-and-architecture.md`
   - `tooling-playbooks.md`
   - `quality-and-dataops.md`

3. **SKILL.md 작성** — references를 얇게 인덱싱, 판단 프레임·절차·산출물 가이드 중심

4. **AGENT.md 작성** — end-to-end 설계 워크플로

5. **plugin.json / README.md 작성**

6. **마켓플레이스 등록**
   - `.claude-plugin/marketplace.json` 갱신
   - 루트 `README.md` 카탈로그 갱신
   - `CHANGELOG.md` 항목 추가
   - 루트 `plugin.json` version bump

7. **검증**
   - 모든 JSON 유효성(`python -m json.tool`)
   - frontmatter·필수 섹션·kebab-case·시크릿 부재 체크
   - (선택) `/sync-specs data-engineer-plugin`으로 local-memory 동기화

## 검증 체크리스트

- [ ] plugin.json 유효 JSON, 메타 정확
- [ ] SKILL/AGENT frontmatter의 description에 한/영 트리거 존재
- [ ] README 필수 섹션 6종 포함
- [ ] references 3종 존재 및 SKILL에서 링크
- [ ] marketplace.json·루트 README·CHANGELOG 갱신
- [ ] 로컬 절대경로·시크릿 미포함

## 리스크 / 메모

- **원문 정합성**: 위키 시리즈 용어(수명주기·저류·Medallion·멱등성 등)를 그대로 사용해 학습 자산과 일관되게.
- **범위 관리**: references는 "실무에서 바로 쓰는 요약"에 집중, 튜토리얼 재작성 금지.
- **ontology-expert와 경계**: 시맨틱/의미 계층·객체·링크·온톨로지는 ontology-expert 소관. 겹치는 지점(Lakehouse·데이터 모델)은 상호 참조로 처리.
