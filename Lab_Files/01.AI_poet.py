import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

while True:
    subject = input("시의 주제를 입력하세요 : (끝내시려면 exit를 입력하세요) ") 

    if subject == "exit":
        break

    poem_content = input("시의 내용을 입력하세요 : ")

    response = openai.chat.completions.create(
                model="dev-gpt-5.4-mini",
                temperature=0.9,
                messages=[
                    {"role":"system","content":"You are a AI poet"},
                    {"role":"user","content": f"시의 주제는 {subject} 시의 내용은 {poem_content} 이 내용으로 시를 지어줘 "}
                ]
    )

    print(response.choices[0].message.content)