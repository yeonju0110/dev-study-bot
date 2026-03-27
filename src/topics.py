import json
import random
from pathlib import Path

# 주제 파일 경로
STATE_FILE = Path(__file__).parent.parent / "data" / "state.json"

# 카테고리별 주제 목록
TOPICS = {
    "OS": ["프로세스 vs 스레드", "컨텍스트 스위칭", "메모리 구조", "페이징", "세마포어/뮤텍스", "데드락"],
    "JVM": ["GC 알고리즘", "힙 구조", "클래스 로더", "JIT 컴파일", "스택 프레임", "메모리 누수"],
    "네트워크": ["TCP/UDP", "3-way handshake", "HTTP/HTTPS", "DNS", "로드밸런서", "CDN"],
    "데이터베이스": ["인덱스", "트랜잭션 ACID", "정규화", "실행계획", "락", "N+1 문제"],
    "자료구조/알고리즘": ["시간복잡도", "트리/그래프 탐색", "동적 프로그래밍", "해시", "정렬"],
    "시스템 설계": ["캐시 전략", "메시지 큐", "MSA vs 모놀리식", "CAP 이론", "샤딩"],
}

# 주제 → 카테고리 역매핑
TOPIC_TO_CATEGORY = {topic: cat for cat, topics in TOPICS.items() for topic in topics}


def load_state() -> dict:
    """state.json에서 주제 이력 로드"""
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """state.json에 주제 이력 저장"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_today_topic(state: dict) -> tuple[str, str, dict, bool]:
    """
    오늘의 주제를 선택하고 상태를 업데이트한다.
    반환값: (topic, category, updated_state, cycle_completed)
    cycle_completed: 전체 순환이 완료되어 리셋된 경우 True
    """
    remaining = state["remaining"]
    used = state["used"]
    cycle_completed = False

    # remaining이 비면 전체 순환 완료 → 리셋
    if not remaining:
        all_topics = list(TOPIC_TO_CATEGORY.keys())
        random.shuffle(all_topics)
        remaining = all_topics
        used = []
        cycle_completed = True

    # remaining에서 랜덤으로 주제 선택
    topic = random.choice(remaining)
    remaining.remove(topic)
    used.append(topic)

    from datetime import date
    updated_state = {
        "used": used,
        "remaining": remaining,
        "last_updated": date.today().isoformat(),
    }

    category = TOPIC_TO_CATEGORY[topic]
    return topic, category, updated_state, cycle_completed
