# pip install agent-framework

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from pydantic import Field
from typing import Annotated
from random import randint

load_dotenv()

def get_weather(location: Annotated[str, Field(
        description="The location to get the weather for. (ex: Seoul, Tokyo... etc)"
)]) -> str:
    conditions = ["sunny","cloudy","rainy","snowy"]
    print(f"Tool called: get_weather for {location}")
    return f"The weather in {location} is {conditions[randint(0,3)]}"

def get_exchange_money(money: Annotated[str, Field(
        description="달러를 한국 돈으로 계산해준다. ex) 10, 20"
)]) -> int:
    korea_won = money * 1510
    print(f"Tool called: get_exchange_money for {money}")
    return korea_won

async def main() -> None:
    print("Hello Agent")

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
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
        tools=[get_weather, get_exchange_money]
    )

    result = await agent.run("10달러는 한국돈으로 얼마니?")
    print(f"Agent: {result}")

if __name__ == "__main__":
    asyncio.run(main())
