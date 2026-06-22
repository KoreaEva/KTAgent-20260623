import openai

OPENAI_API_KEY = ""
AZURE_ENDPOINT = ""
OPENAI_API_TYPE = ""
OPENAI_API_VERSION = ""

openai.api_key = OPENAI_API_KEY
openai.azure_endpoint = AZURE_ENDPOINT
openai.api_type = OPENAI_API_TYPE
openai.api_version = OPENAI_API_VERSION

while True:
    question = input("궁금한 걸 물어보세요 : (끝내시려면 exit를 입력하세요)")

    if question == "exit":
        break

    response = openai.chat.completions.create(
                model="dev-gpt-5.4-mini",
                messages=[
                    {"role":"system","content":"You are a helpufl assistant"},
                    {"role":"user","content":question}
                ]
    )

    print(response.choices[0].message.content)