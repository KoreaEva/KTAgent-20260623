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

    session = agent.create_session()
    
    # result = await agent.run("안녕 반가워 내 이름은 김영욱이야.")
    # print(f"Agent: {result}")
    # result = await agent.run("내가 누구지?")
    # print(f"Agent: {result}")
    
    result = await agent.run("안녕 반가워 내 이름은 김영욱이야.", session=session)
    print(f"Agent: {result}")
    result = await agent.run("내가 누구지?", session=session)
    print(f"Agent: {result}")

if __name__ == "__main__":
    asyncio.run(main())
