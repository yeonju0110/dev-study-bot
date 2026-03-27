import os
import anthropic
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Claude API 설정
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000


class ClaudeAPIError(Exception):
    """Claude API 호출 실패 예외"""
    pass


def generate_content(topic: str, category: str, date: str) -> str:
    """Claude API를 호출해 학습 콘텐츠를 생성한다."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다")

    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = USER_PROMPT_TEMPLATE.format(topic=topic, category=category, date=date)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
    except anthropic.APIError as e:
        raise ClaudeAPIError(f"Claude API 호출 실패: {e}") from e
