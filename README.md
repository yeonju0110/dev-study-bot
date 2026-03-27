# Dev Study Bot

매일 아침 8시, Claude AI가 개발 학습 콘텐츠를 생성해 Discord로 전송하는 자동화 봇.
GitHub Actions로 스케줄링하여 서버 없이 운영한다.

---

## 빠른 시작 (로컬 테스트)

```bash
git clone <repo-url>
cd dev-study-bot

cp .env.example .env
# .env 파일에 실제 키 입력 (아래 발급 방법 참고)

uv sync
uv run --env-file .env python src/main.py
```

---

## GitHub Actions 배포

### 1. Secrets 등록
GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Console에서 발급한 API 키 |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |

`GITHUB_TOKEN`은 자동 제공되므로 별도 등록 불필요.

### 2. 첫 실행 전 확인
- `data/state.json`이 repo에 커밋되어 있어야 함 (기본 포함됨)
- Actions 탭 → **Daily Dev Study Bot** → **Run workflow**로 수동 테스트

### 3. 스케줄
매일 **오전 8시 KST** (UTC 23:00) 자동 실행.
실행 후 `data/state.json`이 자동 커밋되어 주제 이력이 저장됨.

---

## API 키 발급 방법

### Anthropic API 키
1. https://console.anthropic.com 접속
2. **API Keys → Create Key**
3. 발급된 키를 `ANTHROPIC_API_KEY`에 설정

### Discord Webhook URL
1. Discord 서버 → 채널 우클릭 → **채널 편집**
2. **연동 → 웹후크 → 새 웹후크**
3. 이름 설정 후 **웹후크 URL 복사**
4. 복사한 URL을 `DISCORD_WEBHOOK_URL`에 설정

---

## 주제 커스터마이징

`src/topics.py`의 `TOPICS` 딕셔너리에서 카테고리와 주제를 자유롭게 추가/수정할 수 있다.

```python
TOPICS = {
    "OS": ["프로세스 vs 스레드", "컨텍스트 스위칭", ...],
    "JVM": ["GC 알고리즘", "힙 구조", ...],
    # 새 카테고리 추가 가능
}
```

주제를 수정한 뒤에는 `data/state.json`의 `remaining` 목록도 함께 업데이트할 것.

---

## 콘텐츠 / 프롬프트 수정

`src/prompts.py`에서 시스템 프롬프트와 출력 형식을 수정할 수 있다.

---

## 기술 스택

- **Python** 3.11+ / **uv** (패키지 관리)
- **Claude** claude-sonnet-4-20250514 (콘텐츠 생성)
- **Discord Webhook** (전송)
- **GitHub Actions** (스케줄링 + state 자동 커밋)
