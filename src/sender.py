import os
import time
import requests

# Discord 메시지 최대 길이
DISCORD_MAX_LENGTH = 2000
# 재시도 최대 횟수
MAX_RETRIES = 3

# 알림 이모지 매핑
NOTIFICATION_EMOJI = {
    "success": "✅",
    "saved": "🔄",
    "api_error": "❌",
    "send_error": "⚠️",
    "missing_env": "🔑",
    "cycle_complete": "🎉",
}


def _get_webhook_url() -> str:
    """Discord Webhook URL을 환경변수에서 읽는다."""
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        raise EnvironmentError("DISCORD_WEBHOOK_URL 환경변수가 설정되지 않았습니다")
    return url


def _post_message(webhook_url: str, content: str) -> None:
    """
    Discord Webhook으로 단일 메시지를 전송한다.
    실패 시 지수 백오프로 최대 MAX_RETRIES회 재시도한다.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                webhook_url,
                json={"content": content},
                timeout=10,
            )
            response.raise_for_status()
            print(f"[Discord] 메시지 전송 성공 (시도 {attempt}회)")
            return
        except requests.RequestException as e:
            wait = 2 ** (attempt - 1)  # 1s, 2s, 4s
            print(f"[Discord] 전송 실패 (시도 {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                print(f"[Discord] {wait}초 후 재시도...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Discord 전송 실패 ({MAX_RETRIES}회 재시도 후 포기): {e}"
                ) from e


def send_content(content: str) -> None:
    """
    학습 콘텐츠를 Discord로 전송한다.
    2000자를 초과하면 2개 메시지로 분할한다.
    """
    webhook_url = _get_webhook_url()

    if len(content) <= DISCORD_MAX_LENGTH:
        _post_message(webhook_url, content)
    else:
        # 2000자 이내에서 줄바꿈 기준으로 분할
        split_point = content.rfind("\n", 0, DISCORD_MAX_LENGTH)
        if split_point == -1:
            split_point = DISCORD_MAX_LENGTH

        part1 = content[:split_point]
        part2 = content[split_point:].lstrip("\n")

        print("[Discord] 콘텐츠가 2000자 초과 → 2개 메시지로 분할 전송")
        _post_message(webhook_url, part1)
        _post_message(webhook_url, part2)


def send_notification(status: str, message: str) -> None:
    """
    상태 알림을 Discord로 전송한다.
    status: success / saved / api_error / send_error / missing_env / cycle_complete
    """
    emoji = NOTIFICATION_EMOJI.get(status, "ℹ️")
    notification = f"{emoji} {message}"

    try:
        webhook_url = _get_webhook_url()
        _post_message(webhook_url, notification)
    except Exception as e:
        # 알림 전송 실패는 콘솔 출력만 하고 프로세스를 중단하지 않는다
        print(f"[Discord] 알림 전송 실패: {e}")
