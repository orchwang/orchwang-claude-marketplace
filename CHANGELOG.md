# Changelog

이 문서는 orchwang Plugin Marketplace의 모든 주요 변경 사항을 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
버전 관리는 [Semantic Versioning](https://semver.org/lang/ko/)을 사용합니다.

## [Unreleased]

### Added
- `local-memory` 플러그인 추가 — GitHub repo 단위 외부기억을 Obsidian vault에 저장·관리
  - `repo-memory` 에이전트: Pre-flight check, vault 설정, repo name 감지
  - `sync-specs` skill: specs 문서(requirements, specs, plans)를 vault에 동기화
  - `save-idea` skill: 아이디어 메모를 vault에 저장 (태그, 중복 확인 지원)
  - `check-settings` skill: 환경 및 설정 항목 검토, 누락 시 대화형 설정 안내
  - `kepano/obsidian-skills` 플러그인 의존성 연동
- `local-memory` 플러그인 SDD 문서 작성 (`specs/create-local-memory-plugin/`)
- `.claude-plugin/marketplace.json` 마켓플레이스 플러그인 목록 파일 추가

### Changed
- vault 저장 경로를 `{directory}/{repo-name}/` 구조로 변경 (`local-memory.directory` 설정 추가)

### Fixed
- `marketplace.json` 누락으로 인한 플러그인 설치 불가 오류 해결
- `marketplace.json` source 경로 형식 수정 (`./` 접두사 추가)
- `plugin.json` 미지원 키(`dependencies`, `skills`, `agents`) 제거로 스키마 오류 해결

## [1.0.0] - 2026-03-03

### Added
- 마켓플레이스 초기 구성 완료
- `.claude-plugin/plugin.json` 마켓플레이스 메타데이터 생성
- `plugins/` 디렉토리 구조 도입
- `orchwang-general` 플러그인 스켈레톤 등록 (v1.0.0)
- `AGENTS.md` 저장소 가이드라인 작성
- `docs/CONTRIBUTING.md` 기여 가이드 작성

### 등록된 플러그인

| 플러그인 | 버전 | 설명 |
|---------|------|------|
| orchwang-general | 1.0.0 | 범용 Claude Code 플러그인 |
