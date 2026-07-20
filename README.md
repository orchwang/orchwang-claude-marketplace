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
| [orchwang-general](#orchwang-general) | 범용 Claude Code 플러그인 | 1.1.0 | development |
| [local-memory](#local-memory) | GitHub repo 외부기억(specs · scripts · ideas)을 선택 가능한 백엔드에 저장·관리 | 2.1.0 | memory |
| [data-engineer](#data-engineer) | 데이터 엔지니어링 설계·실무 전문가(수명주기·아키텍처·Airflow/dbt/Kafka/Spark/Iceberg) | 1.0.0 | expert |
| [ontology-expert](#ontology-expert) | 온톨로지·시맨틱 레이어 설계 전문가(FDE — 객체·링크·매핑·액션·거버넌스) | 1.0.0 | expert |

### orchwang-general

orchwang 프로젝트를 위한 범용 Claude Code 플러그인입니다. v1.1.0부터 `claude-to-codex-migrator` 스킬을 포함합니다 (`.claude/` 프로젝트 설정을 Codex 호환 스킬 형식으로 변환).

**설치:**
```bash
/plugin install orchwang-general@orchwang-marketplace
```

### local-memory

GitHub repo 단위 외부기억(specs · scripts · ideas)을 선택 가능한 스토리지 백엔드(obsidian / filesystem / git)에 저장·관리하는 플러그인입니다. `datamaker-docs` 같은 git 저장소를 외부기억으로 그대로 사용할 수 있습니다.

**주요 기능:**
- `/sync-specs` — specs 문서(requirements · specs · plans) 동기화
- `/sync-scripts` — 저장소 스크립트(bash · makefile · django-command) 동기화 *(v2.1.0)*
- `/save-idea` — 아이디어 메모 저장
- `/check-settings` — 환경/설정 검토 + 마이그레이션 감사 *(v2.1.0)*

**설치:**
```bash
# obsidian 백엔드를 사용할 경우 의존성 먼저 설치
/plugin install obsidian@kepano/obsidian-skills

# local-memory 설치
/plugin install local-memory@orchwang-marketplace
```

> filesystem / git 백엔드는 추가 의존성 없이 사용할 수 있습니다. 자세한 사용법은 [plugins/local-memory/README.md](./plugins/local-memory/README.md) 참고.

### data-engineer

데이터 엔지니어링 **설계+실무 하이브리드 전문가** 플러그인입니다. 데이터 엔지니어링 수명주기(생성→수집→저장→변환→서빙)와 저류(undercurrents)를 판단 프레임으로 파이프라인·플랫폼을 설계·리뷰·구현하고, Airflow DAG·dbt 모델·Kafka/Spark 코드·Iceberg 테이블 같은 실물 산출물을 만듭니다. `orchwang.github.io` 위키의 Data-Engineering-Essential 시리즈를 증류했습니다.

**구성:** `data-engineer` skill + `data-engineer` agent(end-to-end 설계) + references 3종.

**설치:**
```bash
/plugin install data-engineer@orchwang-marketplace
```

> 자세한 사용법은 [plugins/data-engineer/README.md](./plugins/data-engineer/README.md) 참고.

### ontology-expert

온톨로지·시맨틱 레이어 **설계+실무 하이브리드 전문가**(Palantir식 FDE 관점) 플러그인입니다. "의미 계층 ≠ 물리 데이터 모델"을 원칙으로 도메인을 객체·링크·매핑·액션(write-back)으로 재구성하고, 엔티티 해소·거버넌스까지 설계·리뷰·구현합니다. `orchwang.github.io` 위키의 Ontology-Essential 시리즈를 증류했습니다.

**구성:** `ontology-expert` skill + `ontology-expert` agent(원천→온톨로지 end-to-end) + references 3종.

**설치:**
```bash
/plugin install ontology-expert@orchwang-marketplace
```

> 자세한 사용법은 [plugins/ontology-expert/README.md](./plugins/ontology-expert/README.md) 참고.

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
