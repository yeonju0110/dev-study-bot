import os
import sys
from datetime import date

from .topics import load_state, save_state, get_today_topic
from .generator import generate_content, ClaudeAPIError
from .sender import send_content, send_notification


def check_env() -> None:
    """필수 환경변수 검증. 누락 시 알림 후 종료."""
    missing = [v for v in ("ANTHROPIC_API_KEY", "DISCORD_WEBHOOK_URL") if not os.environ.get(v)]
    if missing:
        msg = f"누락된 환경변수: {', '.join(missing)}"
        print(f"[ERROR] {msg}")
        send_notification("missing_env", msg)
        sys.exit(1)


def main() -> None:
    # 1. 환경변수 검증
    check_env()

    # 2. 주제 선택
    try:
        state = load_state()
        topic, category, updated_state, cycle_completed = get_today_topic(state)
        print(f"[INFO] 오늘의 주제: [{category}] {topic}")
    except Exception as e:
        print(f"[ERROR] 주제 선택 실패: {e}")
        send_notification("api_error", f"주제 선택 중 오류 발생: {e}")
        sys.exit(1)

    # 3. 콘텐츠 생성
    try:
        today = date.today().isoformat()
        content = generate_content(topic, category, today)
        print("[INFO] 콘텐츠 생성 완료")
    except ClaudeAPIError as e:
        print(f"[ERROR] {e}")
        send_notification("api_error", str(e))
        sys.exit(1)

    # 4. Discord 전송
    try:
        send_content(content)
        send_notification("success", f"오늘의 학습 콘텐츠가 전송되었습니다 — [{category}] {topic}")
        print("[INFO] Discord 전송 완료")
    except Exception as e:
        print(f"[ERROR] Discord 전송 실패: {e}")
        send_notification("send_error", str(e))
        sys.exit(1)

    # 5. 전체 순환 완료 알림
    if cycle_completed:
        send_notification("cycle_complete", "모든 주제를 학습했습니다! 처음부터 다시 시작합니다 🎉")

    # 6. 상태 저장 (GitHub Actions가 커밋)
    try:
        save_state(updated_state)
        remaining_count = len(updated_state["remaining"])
        send_notification("saved", f"주제 이력이 저장되었습니다 — 남은 주제 {remaining_count}개")
        print(f"[INFO] state.json 저장 완료 (남은 주제: {remaining_count}개)")
    except Exception as e:
        print(f"[ERROR] state.json 저장 실패: {e}")
        send_notification("send_error", f"state.json 저장 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
