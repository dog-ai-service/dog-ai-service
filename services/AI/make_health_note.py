import os
from datetime import date
#사이드바 로그인
from services.drive_healthnote_api import *
import json
import openai

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def make_health_note(prompt):
    today = date.today().isoformat()

    health_note_prompt = f"""
    사용자가 입력한 강아지의 증상:
    "{prompt}"

    아래 형식으로 증상을 추출해줘. 날짜는 오늘날짜인 {today}로 해줘.
    부가적인 설명은 필요없이 아래 형식으로만 결과를 줘.

    {{
        "날짜": "2025-05-21", 
        "주요 증상" : "눈 붓기, 눈 충혈, 귀 긁기", 
        "의심 질병" : " 알레르기, 결막염, 귀 염증", 
        "필요한 조치" : "병원 방문 권장, 알레르기 유발 물질 확인, 귀 청소", 
        "추가 메모" : "증상이 지속되거나 악화될 경우 즉시 병원 방문 권장"
    }}
    주의할점은, 딕셔너리의 key값은 ""로 감싸야해.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 강아지 증상을 json 형식으로 바꾸어주는 보조야. 사용자 프롬프트를 json 형식으로 바꾸어줘."},
            {"role": "user", "content": health_note_prompt}
        ],
        temperature=0.1
    )
    text = response.choices[0].message.content
    return json.loads(text)