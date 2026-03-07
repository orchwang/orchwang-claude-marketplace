# orchwang Plugin Marketplace

orchwang 프로젝트 개발을 위한 개인 Claude Code 플러그인 마켓플레이스입니다.

## 개요

이 마켓플레이스는 orchwang 프로젝트 개발에 필요한 Claude Code 플러그인의 중앙 등록소입니다.

## 빠른 시작

### 1. 마켓플레이스 추가

```bash
/plugin marketplace add orchwang/orchwang-claude-marketplace
```

### 2. 사용 가능한 플러그인 탐색

```bash
/plugin > Discover
```

### 3. 플러그인 설치

```bash
# 범용 개발 도구
/plugin install orchwang-general@orchwang-marketplace
```

## 사용 가능한 플러그인

| 플러그인 | 설명 | 버전 | 카테고리 |
|---------|------|------|----------|
| [orchwang-general](#orchwang-general) | 범용 Claude Code 플러그인 | 1.0.0 | development |
| [local-memory](#local-memory) | GitHub repo 외부기억을 Obsidian vault에 저장·관리 | 1.0.0 | memory |

### orchwang-general

orchwang 프로젝트를 위한 범용 Claude Code 플러그인입니다.

> 현재 스켈레톤 상태이며, 기능이 순차적으로 추가될 예정입니다.

**설치:**
```bash
/plugin install orchwang-general@orchwang-marketplace
```

### local-memory

GitHub repo 단위 외부기억을 Obsidian vault에 저장·관리하는 플러그인입니다. specs 문서 동기화, 아이디어 메모 저장 기능을 제공합니다.

> 의존성: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

**설치:**
```bash
# 의존성 먼저 설치
/plugin install obsidian@kepano/obsidian-skills

# local-memory 설치
/plugin install local-memory@orchwang-marketplace
```

## 요구 사항

- Claude Code v2.1.0 이상
- `GITHUB_TOKEN` 환경 변수 (private 저장소 접근용)

## 문제 해결

### 마켓플레이스가 인식되지 않는 경우

```bash
# Claude Code 버전 확인
claude --version

# 마켓플레이스 재등록
/plugin marketplace remove orchwang-marketplace
/plugin marketplace add orchwang/orchwang-claude-marketplace
```

### 플러그인 설치 실패

```bash
# GITHUB_TOKEN 설정 확인
echo $GITHUB_TOKEN

# 토큰에 repo 권한이 있는지 확인
gh auth status
```

## 라이선스

MIT
