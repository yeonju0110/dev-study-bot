# Dev Study Bot — 구현 명세서

## 프로젝트 개요
매일 아침 Claude API로 개발 학습 콘텐츠를 생성하고, Discord Webhook으로 전송하는 자동화 봇.
GitHub Actions로 스케줄링하여 서버 없이 운영한다.

---

## 기술 스택
- **언어**: Python 3.11+
- **패키지 관리**: uv
- **콘텐츠 생성**: Claude API (`claude-sonnet-4-20250514`)
- **전송**: Discord Webhook (HTTP POST)
- **스케줄링**: GitHub Actions cron (매일 오전 8시 KST)
- **시크릿 관리**: GitHub Secrets

---

## 디렉토리 구조
```
dev-study-bot/
├── .github/
│   └── workflows/
│       └── daily.yml
├── docs/
│   └── spec.md         # 이 문서
├── src/
│   ├── main.py         # 진입점
│   ├── generator.py    # Claude API 호출 및 콘텐츠 생성
│   ├── sender.py       # Discord Webhook 전송
│   ├── topics.py       # 주제 로테이션 관리
│   └── prompts.py      # 시스템 프롬프트 및 유저 프롬프트 템플릿
├── data/
│   ├── topics.json     # 주제 목록 (카테고리별)
│   └── state.json      # 주제 이력 (repo에 커밋으로 영구 보존)
├── pyproject.toml
└── README.md
```

---

## 주제 로테이션 (`topics.py`)

아래 주제들을 **순서 없이 랜덤**하게 순환한다.
같은 주제가 연속으로 나오지 않도록 처리한다.
주제가 한 바퀴 돌면 다시 섞어서 반복한다.

### 주제 목록
| 카테고리 | 세부 주제 |
|---|---|
| OS | 프로세스 vs 스레드, 컨텍스트 스위칭, 메모리 구조, 페이징, 세마포어/뮤텍스, 데드락 |
| JVM | GC 알고리즘, 힙 구조, 클래스 로더, JIT 컴파일, 스택 프레임, 메모리 누수 |
| 네트워크 | TCP/UDP, 3-way handshake, HTTP/HTTPS, DNS, 로드밸런서, CDN |
| 데이터베이스 | 인덱스, 트랜잭션 ACID, 정규화, 실행계획, 락, N+1 문제 |
| 자료구조/알고리즘 | 시간복잡도, 트리/그래프 탐색, 동적 프로그래밍, 해시, 정렬 |
| 시스템 설계 | 캐시 전략, 메시지 큐, MSA vs 모놀리식, CAP 이론, 샤딩 |

### 로테이션 상태 관리
상태 파일 `data/state.json`을 repo에 커밋하여 주제 이력을 영구 보존한다.

**`data/state.json` 구조**
```json
{
  "used": ["프로세스 vs 스레드", "GC 알고리즘"],
  "remaining": ["TCP/UDP", "인덱스", "..."],
  "last_updated": "2026-03-27"
}
```

**동작 방식**
1. `remaining` 리스트에서 랜덤으로 오늘 주제 1개 선택
2. 선택한 주제를 `used`로 이동, `remaining`에서 제거
3. `remaining`이 비면 `used` 전체를 다시 셔플해서 `remaining`으로 리셋 (완전 순환)
4. 업데이트된 `state.json`을 GitHub Actions에서 repo에 자동 커밋

---

## 콘텐츠 생성 (`generator.py`, `prompts.py`)

### Claude API 호출 스펙
- 모델: `claude-sonnet-4-20250514`
- max_tokens: 4000
- 언어: **한국어**
- 난이도: **시니어 목표** (설계 의도·트레이드오프·실무 판단까지 포함)

### 출력 형식
```
📅 날짜 | 카테고리 | 주제

⏰ 한 줄 핵심
🔍 왜 이게 필요했나? (설계 배경)
🧠 핵심 원리
⚖️ 트레이드오프
💡 실무 판단 기준
❓ 생각해볼 질문 (Discord 스포일러 태그로 해설 숨김)
📌 연결 개념
```

---

## Discord 전송 (`sender.py`)

### 스펙
- Discord Webhook URL은 환경변수 `DISCORD_WEBHOOK_URL`에서 읽는다.
- 콘텐츠가 Discord 메시지 길이 제한(2000자)을 초과할 경우 **2개 메시지로 분할**해서 전송한다.
- 전송 실패 시 최대 3회 재시도 (지수 백오프: 1s → 2s → 4s).
- 전송 성공/실패 여부를 콘솔에 로그 출력.

### 알림 목록
| 상황 | 알림 내용 | 이모지 |
|---|---|---|
| 콘텐츠 전송 성공 | "오늘의 학습 콘텐츠가 전송되었습니다" + 주제명 | ✅ |
| `state.json` 커밋 완료 | "주제 이력이 저장되었습니다" + 남은 주제 수 | 🔄 |
| Claude API 실패 | 에러 메시지 전문 | ❌ |
| Discord 전송 실패 | 재시도 횟수 + 에러 내용 | ⚠️ |
| 환경변수 누락 | 누락된 변수명 | 🔑 |
| 주제 전체 순환 완료 | "모든 주제를 학습했습니다! 처음부터 다시 시작합니다" | 🎉 |

---

## GitHub Actions (`daily.yml`)

### 스케줄
- 매일 **오전 8시 KST** (= UTC 23:00 전날)
- 수동 실행(`workflow_dispatch`) 가능

### Secrets 목록
| Secret 이름 | 설명 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API 키 |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |
| `GITHUB_TOKEN` | 자동 제공 (별도 설정 불필요) |

### 워크플로우 흐름
1. uv 셋업 (Python 3.11)
2. `uv sync --frozen`
3. `uv run python -m src.main` 실행
4. `data/state.json` 변경사항 감지
5. 변경된 경우 repo에 자동 커밋 & push (`chore: update study state (YYYY-MM-DD)`)

---

## 예외 처리
- Claude API 호출 실패 → Discord 알림 전송 후 종료
- Discord 전송 실패 → 3회 재시도 후 GitHub Actions 로그에 에러 출력
- 환경변수 누락 → Discord 알림 + 명확한 에러 메시지와 함께 즉시 종료
- 모든 예외는 `try/except`로 감싸고 GitHub Actions 로그에도 함께 출력

---

## 구현 유의사항
- 외부 라이브러리는 `anthropic`, `requests` 두 개만 사용 (최소 의존성)
- 모든 코드에 한국어 주석 작성
- `main.py`는 50줄 이내로 간결하게 유지
- 하드코딩 금지 — 모든 설정값은 환경변수 또는 `data/topics.json`으로 관리
- 프롬프트는 `prompts.py`에서 단독 관리
