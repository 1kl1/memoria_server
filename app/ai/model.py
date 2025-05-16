from langchain_anthropic import ChatAnthropic
from app.config import settings

claude_llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    anthropic_api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.2
)