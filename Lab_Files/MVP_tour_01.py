# pip install agent-framework

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    model = os.getenv("AZURE_OPENAI_CHAT_MODEL")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")

    azure_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )

    agent = OpenAIChatClient(
        model=model,
        async_client=azure_client,
    ).as_agent(
        name="MVPTour-Assistant",
        instructions="""
        당신은 여행사 'MVP Tour'의 20년 경력의 상담원입니다.
        고객에게 정중하게 인사하고, 여행 계획에 대해 도움을 줄 준비가 되었음을 알리세요
        답변 끝에는 항상 '즐거운 여행의 시작, MVP Tour입니다!'라는 문구를 붙여주세요.
        """
    )

    print(f"에이전트 {agent.name}이 준비 되었습니다.")

    user_input = "안녕하세요! 도쿄 여행 패키지를 추천해주세요"
    print(f"\n[나]: {user_input}")

    result = await agent.run(user_input)
    print(f"\n[MVP Tour 상담원]: {result}")

    #Stream Output
    # async for update in agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘", stream=True):
    #     if update.text:
    #         print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
