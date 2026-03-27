import json
import random
from datetime import date
from pathlib import Path

# 데이터 파일 경로
_DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = _DATA_DIR / "state.json"
TOPICS_FILE = _DATA_DIR / "topics.json"


def _load_topics() -> dict:
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


TOPICS = _load_topics()

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

    updated_state = {
        "used": used,
        "remaining": remaining,
        "last_updated": date.today().isoformat(),
    }

    category = TOPIC_TO_CATEGORY[topic]
    return topic, category, updated_state, cycle_completed
