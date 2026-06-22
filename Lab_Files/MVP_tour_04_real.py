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
import requests

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

# [도구 1] 날씨 조회 함수
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="날씨를 확인하려는 도시 또는 지역명")]
) -> str:
    """지정된 지역의 현재 날씨 정보를 가져옵니다."""
    print(f"🔍 [시스템] 날씨 도구 호출 중: {location}")
    
    try:
        # 지역명으로 좌표 검색
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=ko"
        geo_response = requests.get(geocoding_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"❌ '{location}'을(를) 찾을 수 없습니다. 다른 도시명으로 시도해주세요."
        
        # 첫 번째 결과 사용
        location_info = geo_data['results'][0]
        latitude = location_info['latitude']
        longitude = location_info['longitude']
        city = location_info['name']
        country = location_info.get('country', '')
        
        # 현재 날씨 조회
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code,wind_speed_10m&temperature_unit=celsius"
        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        current = weather_data['current']
        temperature = current['temperature_2m']
        weather_code = current['weather_code']
        wind_speed = current['wind_speed_10m']
        
        # 날씨 코드를 한글로 변환
        weather_descriptions = {
            0: "맑음", 1: "맑음", 2: "부분 구름", 3: "흐림",
            45: "안개", 48: "안개",
            51: "이슬비", 53: "이슬비", 55: "이슬비",
            61: "약한 비", 63: "비", 65: "강한 비",
            71: "가벼운 눈", 73: "눈", 75: "무거운 눈",
            77: "눈 입자", 80: "약한 빗방울", 81: "가끔 빗방울", 82: "무거운 빗방울",
            85: "가벼운 눈 소나기", 86: "무거운 눈 소나기",
            95: "폭풍우", 96: "폭풍우와 우박", 99: "폭풍우와 큰 우박"
        }
        
        weather_desc = weather_descriptions.get(weather_code, "알 수 없음")
        
        return f"📍 {city}, {country}\n🌡️ 현재 기온: {temperature}°C\n☁️ 날씨: {weather_desc}\n💨 풍속: {wind_speed} km/h"
        
    except requests.exceptions.Timeout:
        return "❌ 날씨 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"❌ 날씨 정보를 가져올 수 없습니다. 오류: {str(e)}"
    except Exception as e:
        return f"❌ 날씨 조회 중 오류가 발생했습니다: {str(e)}"

# [도구 2] 환율 조회 함수
@tool(approval_mode="never_require")
def get_exchange_rate(
    base_currency: Annotated[str, Field(description="기준 통화 코드 (예: USD, EUR)")],
    target_currency: Annotated[str, Field(description="대상 통화 코드 (예: KRW, JPY)")]
) -> str:
    """두 통화 간의 실시간 환율 정보를 가져옵니다."""
    print(f"🔍 [시스템] 환율 도구 호출 중: {base_currency} -> {target_currency}")
    
    try:
        # 실시간 환율 API 호출
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            return f"현재 {base_currency} 대비 {target_currency}의 환율은 {rate:.2f}입니다."
        else:
            return f"❌ {target_currency} 통화 코드를 찾을 수 없습니다. 올바른 통화 코드를 입력해주세요."
    except requests.exceptions.Timeout:
        return "❌ 환율 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"❌ 환율 정보를 가져올 수 없습니다. 오류: {str(e)}"
    except Exception as e:
        return f"❌ 환율 조회 중 오류가 발생했습니다: {str(e)}"
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
    
    user_input = "지금 서울의 날씨는 어떠니 그리고 원달러 환율은 얼마이니?"
    print(f"\n[나]: {user_input}")

    result = await agent.run(user_input)
    print(f"\n[MVP Tour 상담원]: {result}")

    #Stream Output
    # async for update in agent.run("왜 파이썬은 인기가 많은지 자세히 설명해줘", stream=True):
    #     if update.text:
    #         print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
