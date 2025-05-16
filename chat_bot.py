import streamlit as st
from streamlit_calendar import calendar
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, load_tools, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain_core.outputs import LLMResult
from typing import Any
from datetime import timedelta, datetime
# LLM 모델 출력값 파싱 처리, 문자열 형태일 때 사용할 수 있는 파서
from langchain_core.output_parsers import StrOutputParser
# 프럼프트
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
import re
import time

load_dotenv()
# print(os.environ['OPENAI_API_KEY'])

CHAT_UPDATE_INTERVAL_SECOND = 1
user_name = "홍길동"
dog_data =[
    {
        'name':'청이', 
        'age':'8', 
        'dog_type':'포메라니안', 
        'weight':'4.7', 
        'memo':'슬개골 주의, 분리불안, 식욕이 별로없음'
    }
]


# 페이지 설정
st.set_page_config(page_title="반려견과 보호자를 위한 AI 비서", layout="wide")

def chat_stream(response):
    for char in response:
        yield char
        time.sleep(0.02)


def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

def init_chat():
    if "history" not in st.session_state:
        st.session_state.history = []

    for i, message in enumerate(st.session_state.history):
        
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant":
                feedback = message.get("feedback", None)
                st.session_state[f"feedback_{i}"] = feedback
                st.feedback(
                    "thumbs",
                    key=f"feedback_{i}",
                    disabled=feedback is not None,
                    on_change=save_feedback,
                    args=[i],
                )

    if prompt := st.chat_input("Say something"):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            cb = StreamlitCallbackHandler(st.container())
            agent_chain = init_agent_chain(st.session_state.history)
            res = agent_chain.invoke(
                    {"input":prompt},  # 사용자의 질의
                    {"callbacks":[cb]} # 콜백
                )
            response = st.write_stream(chat_stream(res['output']))
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.history)}",
                on_change=save_feedback,
                args=[len(st.session_state.history)],
            )
        st.session_state.history.append({"role": "assistant", "content": response})
        # print("user : ", prompt)
        # print("ai : ", response)
        # print("history : ", st.session_state.history)

def init_agent_chain(history):
    llm = ChatOpenAI(model_name  = os.environ['OPENAI_API_MODEL'], temperature = os.environ['OPENAI_API_TEMPERATURE'])
    tools = load_tools([#"ddg-search", 
                        "wikipedia"])
    hub_tool = hub.pull('hwchase17/openai-tools-agent')
    memory = ConversationBufferMemory(chat_memory=history, 
                                      memory_key='my_first_chat',
                                      return_messages=True
                                      )
    agent = create_openai_tools_agent(llm, tools, hub_tool)
    return AgentExecutor(agent=agent, tools=tools, memory=memory)

# 샘플 캘린더
def init_calendar():
    # 캘린더 이벤트 샘플
    events = [
        {"title": "소화제 뭉이 복용", "start": "2025-05-15", "end": "2025-05-15"},
        {"title": "사료 뭉이 바뀜", "start": "2025-05-15", "end": "2025-05-15"},
        {"title": "건강노트 기록", "start": "2025-05-16", "end": "2025-05-16"},
        {"title": "목욕 뭉이", "start": "2025-05-17", "end": "2025-05-17"},
        {"title": "매달 건강검진", "start": "2025-05-24", "end": "2025-05-24"},
    ]

    # 캘린더 렌더링
    calendar_options = {
        "initialView": "dayGridMonth",
        "locale": "ko",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }
    calendar(events=events, options=calendar_options)


def init_main():
    # 사이드바 메뉴
    with st.sidebar:
        st.header(f"{user_name} 님 환영합니다")
        menu = st.radio("메뉴 선택", ["캘린더", "챗봇", "건강노트", "사용자 정보"])

    # 메인 영역
    st.title(menu)

    # 챗봇 메뉴 선택 시 챗봇 UI 표시
    if menu == "챗봇":
        st.markdown("---")
        init_chat()

    elif menu == "캘린더":
        st.markdown("---")
        init_calendar()


if __name__ == '__main__':
    init_main()