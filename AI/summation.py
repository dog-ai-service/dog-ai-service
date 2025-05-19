'''
    사용자가 일정 요약 버튼을 눌렀을때, 일정을 요약해줌.
'''

import openai
import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import StreamlitCallbackHandler

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])



def summation(user_input):
    prompt = f"""
    오늘 견주의 일정은 아래와 같아. 
    {user_input}

    다음 일정을 요약해서 알려줘. 
    만약 겹치는 일정이 있으면 언제 어떤 것들이 겹치는지 자세하게 알려줘. 
    """

    cb = StreamlitCallbackHandler(st.container())

    llm = ChatOpenAI(
        model_name=os.environ['OPENAI_API_MODEL'],
        temperature=os.environ['OPENAI_API_TEMPERATURE'],
        streaming=True,
        callbacks=[cb]  
    )
    response = llm.invoke(prompt)

    return response

