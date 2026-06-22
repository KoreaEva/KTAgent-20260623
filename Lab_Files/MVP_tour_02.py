# pip install agent-framework

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from typing import Annotated
from pydantic import Field
from random import randint
from agent_framework import tool

load_dotenv()

# [도구1] 날씨 조회 함수
@tool(approval_mode="never_require")
def get_weather(
        location: Annotated[str, Field(description="날씨를 확인하려는 도시 또는 지역명 (ex: 서울, 부산 등등)")]
) -> str:
    """지정된 지역의 현재 날씨 정보를 가져옵니다."""
    conditions = ["맑음","흐림","비","폭풍우"]
    print(f"[도구] 날씨 도구 호출 중: {location}")

    return f"{location}의 날씨는 {conditions[randint(0,3)]}이며, 기온은 {randint(10,30)}도 입니다."

# [도구2] 환율 조회 함수 
@tool(approval_mode="never_require")
def get_exchange_rate(
    base_currency: Annotated[str, Field(description="기준 통화 코드 (예: USD, EUR)")], 
    target_currency: Annotated[str, Field(description="대상 통화 코드 (예: KRW, JPY)")]
) -> str:
    """두 통화 간의 실시간 환율 정보를 가져옵니다."""
    print(f"[도구] 환율 도구 호출 중: {base_currency} -> {target_currency}")

    if target_currency == "KRW":
        rate = randint(1500, 1600) / 100
    else:
        rate = randint(80, 150) / 100

    return f"현재 {base_currency} 대비 {target_currency}의 환율은 {rate} 입니다."


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
        """,
        tools=[get_weather, get_exchange_rate]
    )

    print(f"에이전트 {agent.name}이 준비 되었습니다.")

    # user_input = "서울의 날씨는 어떠니?"
    # print(f"\n[나]: {user_input}")

    # result = await agent.run(user_input)
    # print(f"\n[MVP Tour 상담원]: {result}")

    # user_input = "지금 원화 대비 달러의 환율은 어떤가요?"
    # print(f"\n[나]: {user_input}")

    # result = await agent.run(user_input)
    # print(f"\n[MVP Tour 상담원]: {result}")
    
    user_input = "서울로 여행을 가려고 하는데 지금 서울의 날씨는 어떠하니? 그리고 지금 100달러가 있는데 환화로 얼마가 되니?"
    print(f"\n[나]: {user_input}")

    result = await agent.run(user_input)
    print(f"\n[MVP Tour 상담원]: {result}")

    #Stream Output
    # async for update in agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘", stream=True):
    #     if update.text:
    #         print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
