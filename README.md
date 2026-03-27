# 🧠 Dev Study Bot — 개발 명세서

## 프로젝트 개요
매일 아침 Claude API로 개발 학습 콘텐츠를 생성하고, Discord Webhook으로 전송하는 자동화 봇.
GitHub Actions로 스케줄링하여 서버 없이 운영한다.

---

## 기술 스택
- **언어**: Python 3.11+
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
├── src/
│   ├── main.py         # 진입점
│   ├── generator.py    # Claude API 호출 및 콘텐츠 생성
│   ├── sender.py       # Discord Webhook 전송
│   └── topics.py       # 주제 로테이션 관리
├── data/
│   └── state.json      # 주제 이력 (repo에 커밋으로 영구 보존)
├── requirements.txt
└── README.md
```

---

## 주제 로테이션 (`topics.py`)

아래 주제들을 **순서 없이 랜덤**하게 순환한다.
같은 주제가 연속으로 나오지 않도록 처리한다.
주제가 한 바퀴 돌면 다시 섞어서 반복한다.

### 주제 목록
| 카테고리 | 세부 주제 예시 |
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
  "used": ["프로세스 vs 스레드", "GC 알고리즘", "..."],
  "remaining": ["TCP/UDP", "인덱스", "..."],
  "last_updated": "2026-03-27"
}
```

**동작 방식**
1. `remaining` 리스트에서 랜덤으로 오늘 주제 1개 선택
2. 선택한 주제를 `used`로 이동, `remaining`에서 제거
3. `remaining`이 비면 `used` 전체를 다시 셔플해서 `remaining`으로 리셋 (완전 순환)
4. 업데이트된 `state.json`을 GitHub Actions에서 repo에 자동 커밋

**GitHub Actions 커밋 설정**
- `actions/checkout`에 `token: ${{ secrets.GITHUB_TOKEN }}` 사용
- 커밋 메시지: `chore: update study state (2026-03-27)`
- `data/state.json` 초기 파일은 직접 repo에 push해서 세팅

---

## 콘텐츠 생성 (`generator.py`)

### Claude API 호출 스펙
- 모델: `claude-sonnet-4-20250514`
- max_tokens: 2000
- 언어: **한국어**
- 난이도: **중급** (기본 개념은 알지만 깊이 있는 이해가 부족한 개발자 대상)

### 시스템 프롬프트
```
당신은 개발자를 위한 기술 학습 콘텐츠 작성 전문가입니다.
매일 아침 개발자가 출근 전 10분 안에 읽을 수 있는 분량으로,
중급 개발자 수준의 깊이 있는 학습 콘텐츠를 작성합니다.
설명은 친근하고 명확하게, 비유를 적극 활용해주세요.
```

### 유저 프롬프트 템플릿
```
오늘의 주제: {topic}
날짜: {date}

아래 형식에 맞춰 학습 콘텐츠를 작성해주세요.

[형식]
**📅 {date} | {category} | {topic}**

**⏰ 3줄 요약**
• 요약 1
• 요약 2
• 요약 3

**🧠 핵심 개념**
(300~400자 분량. 비유와 예시를 포함해 중급 개발자가 "아, 그런 거구나!" 할 수 있도록 설명)

**💡 실무에서는?**
(실제 개발 현장에서 이 개념이 어떻게 적용되는지 1~2가지 예시)

**❓ 오늘의 퀴즈**
질문: (개념을 제대로 이해했는지 확인하는 질문 1개)
<details>
<summary>정답 보기</summary>
정답: (간결한 정답)
</details>

**🔍 더 파고들기**
키워드: (관련 심화 키워드 3개)
```

---

## Discord 전송 (`sender.py`)

### 스펙
- Discord Webhook URL은 환경변수 `DISCORD_WEBHOOK_URL`에서 읽는다.
- 콘텐츠가 Discord 메시지 길이 제한(2000자)을 초과할 경우 **2개 메시지로 분할**해서 전송한다.
- 전송 실패 시 최대 3회 재시도 (지수 백오프).
- 전송 성공/실패 여부를 콘솔에 로그 출력.

---

## GitHub Actions (`daily.yml`)

### 스케줄
- 매일 **오전 8시 KST** (= UTC 23:00 전날)
- 수동 실행(`workflow_dispatch`)도 가능하게 설정

### Secrets 목록
| Secret 이름 | 설명 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API 키 |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |
| `GITHUB_TOKEN` | 자동 제공 (별도 설정 불필요) |

### 워크플로우 흐름
1. Python 3.11 셋업
2. `pip install -r requirements.txt`
3. `python src/main.py` 실행
4. `data/state.json` 변경사항 감지
5. 변경된 경우 repo에 자동 커밋 & push

---

## requirements.txt
```
anthropic
requests
```

---

## Discord 알림 (`sender.py`)

학습 콘텐츠 전송 외에, 아래 상황에도 Discord로 별도 알림을 보낸다.
알림은 `send_notification(status, message)` 함수로 통합 관리한다.

| 상황 | 알림 내용 | 이모지 |
|---|---|---|
| 콘텐츠 전송 성공 | "오늘의 학습 콘텐츠가 전송되었습니다" + 주제명 | ✅ |
| `state.json` 커밋 완료 | "주제 이력이 저장되었습니다" + 남은 주제 수 | 🔄 |
| Claude API 실패 | 에러 메시지 전문 | ❌ |
| Discord 전송 실패 | 재시도 횟수 + 에러 내용 | ⚠️ |
| 환경변수 누락 | 누락된 변수명 | 🔑 |
| 주제 전체 순환 완료 | "모든 주제를 학습했습니다! 처음부터 다시 시작합니다" | 🎉 |

---

## 예외 처리
- Claude API 호출 실패 → Discord 알림 전송 후 종료
- Discord 전송 실패 → 3회 재시도 (지수 백오프) 후 GitHub Actions 로그에 에러 출력
- 환경변수 누락 → Discord 알림 + 명확한 에러 메시지와 함께 즉시 종료
- 모든 예외는 `try/except`로 감싸고 GitHub Actions 로그에도 함께 출력

---

## 구현 시 유의사항
- 외부 라이브러리는 `anthropic`, `requests` 두 개만 사용한다 (최소 의존성)
- 모든 코드에 한국어 주석 작성
- `main.py`는 50줄 이내로 간결하게 유지
- 하드코딩 금지 — 모든 설정값은 환경변수 또는 `topics.py` 상수로 관리