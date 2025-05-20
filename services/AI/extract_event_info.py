'''
    사용자가 자연어로 프롬프트 입력하면 해당 프롬프트를 특정 구조로 만드는 함수
'''

import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])



def extract_event_info(user_input: str, date):
    prompt = f"""
    사용자가 다음과 같이 말했어: "{user_input}"
    아래 형식으로 일정을 추출해줘. 기준은 오늘날짜인 {date}로 해줘.
    부가적인 설명은 필요없이 아래 형식으로만 결과를 줘.
    
    {{
        "summary": "일정 제목",
        "start": "2025-05-20T15:00:00",
        "end": "2025-05-20T16:00:00"
    }}

    만약, 여러개의 일정을 요구하면 아래 형식으로 추출해줘. 

    {[{
        "summary": "일정 제목",
        "start": "2025-05-20T15:00:00",
        "end": "2025-05-20T16:00:00"
    },
    {
        "summary": "일정 제목",
        "start": "2025-05-20T15:00:00",
        "end": "2025-05-20T16:00:00"
    },
    ...]}

    주의할점은, 딕셔너리의 key값은 ""로 감싸야해.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 일정 보조야. 자연어를 시간 정보로 바꿔줘."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content