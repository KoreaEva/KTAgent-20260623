# pip install agent-framework

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

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
    )

    #result = await agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘")
    #print(f"Agent: {result}")

    #Stream Output
    async for update in agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘", stream=True):
        if update.text:
            print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
