# pip install agent-framework
# pip install chromadb

import asyncio
import os

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from typing import Annotated
from pydantic import Field
from random import randint
from agent_framework import tool
import chromadb

load_dotenv()

# ChromaDB 클라이언 설정
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="mvp_tour_info")

# 테스트용 사내 지식 데이터 추가 
collection.add(
    documents=[
        "시애틀 투어 패키지: 3박 4일 일정으로 스페이스 니들 입장권이 포함되어 있습니다.",
        "MVP Tour 특별 환전 서비스: 본사 1층에서 오전 9시부터 오후 4시까지 우대 환율을 제공합니다.",
        "예약 취소 규정: 여행 7일전까지는 100% 환불 가능하며, 이후에는 50%의 수수료가 발생합니다."
    ],
    ids = ["doc1","doc2","doc3"]
)
print("사내 지식 베이스 구축 완료")

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

# [도구3] RAG
@tool(approval_mode="never_require")
def search_travel_docs(query: Annotated[str,
                    Field(description="여행 상품이나 회사 규정에 대해 검색할 키워드")])->str:
    """사내 지식베이스(ChromaDB)에서 여행 상품 및 정책 정보를 검색합니다."""
    print(f"[도구] RAG 지식베이스 검색 중: '{query}'")

    # 유사도 기반의 검색
    result = collection.query(query_texts=[query],n_results=1)

    if result['documents'][0]:
        return f"관련 정보 검색 결과: {result['documents'][0][0]}"
    else:
        return "관련된 정보를 찾을 수 없습니다. "


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
        tools=[get_weather, get_exchange_rate, search_travel_docs]
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
    
    user_input = "시애틀로 여행을 가려고 하는데 지금 시애틀의 날씨는 어떠하니? 그리고 시애틀 투어 패키지 구성은 어떻게 되니?"
    print(f"\n[나]: {user_input}")

    result = await agent.run(user_input)
    print(f"\n[MVP Tour 상담원]: {result}")

    #Stream Output
    # async for update in agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘", stream=True):
    #     if update.text:
    #         print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
