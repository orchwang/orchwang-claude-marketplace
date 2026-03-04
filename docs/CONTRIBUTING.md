# 기여 가이드

orchwang Plugin Marketplace에 기여해 주셔서 감사합니다.

## 플러그인 구조

모든 플러그인은 아래 구조를 따라야 합니다:

```
plugins/<plugin-name>/
  plugin.json          # 플러그인 매니페스트 (필수)
  README.md            # 플러그인 문서 (필수)
  commands/            # 슬래시 명령어 (*.md)
  skills/              # 스킬 모듈
  agents/              # 에이전트 플레이북
```

## 네이밍 규칙

- 플러그인 이름: kebab-case (예: `orchwang-general`)
- 폴더 이름: kebab-case
- 명령어 파일: kebab-case `.md` 파일

## 새 플러그인 추가 절차

1. `plugins/<plugin-name>/` 디렉토리 생성
2. `plugin.json` 매니페스트 작성
3. `README.md` 작성 (개요, 설치, 명령어, 스킬, 에이전트, 빠른 시작, 라이선스 섹션 포함)
4. 필요한 하위 디렉토리 생성 (`commands/`, `skills/`, `agents/`)
5. `.claude-plugin/plugin.json`에 플러그인 등록
6. `README.md` 플러그인 목록 업데이트
7. `CHANGELOG.md`에 변경 사항 기록

## plugin.json 스키마

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "플러그인 설명",
  "author": { "name": "orchwang" },
  "homepage": "https://github.com/orchwang/orchwang-claude-marketplace",
  "repository": "https://github.com/orchwang/orchwang-claude-marketplace.git",
  "license": "MIT",
  "keywords": [],
  "commands": [],
  "skills": [],
  "agents": []
}
```

## 코드 리뷰 체크리스트

- [ ] `plugin.json`이 유효한 JSON인가?
- [ ] README에 필수 섹션이 모두 포함되어 있는가?
- [ ] 시크릿이나 로컬 경로가 포함되어 있지 않은가?
- [ ] kebab-case 네이밍 규칙을 따르고 있는가?
- [ ] CHANGELOG에 변경 사항이 기록되어 있는가?

## 커밋 메시지

짧고 명령형 메시지를 사용합니다:

```
feat: add orchwang-general plugin
docs: update README plugin catalog
fix: correct plugin.json schema
```

## 라이선스

이 저장소에 기여함으로써, 기여분이 MIT 라이선스 하에 배포됨에 동의합니다.
