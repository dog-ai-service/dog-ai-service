import streamlit as st
from streamlit_calendar import calendar
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, load_tools, create_openai_tools_agent, ConversationalChatAgent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain_core.outputs import LLMResult
from typing import Any
from datetime import timedelta, datetime
# LLM 모델 출력값 파싱 처리, 문자열 형태일 때 사용할 수 있는 파서
from langchain_core.output_parsers import StrOutputParser
# 프럼프트
# from langchain_core.msgs import ChatmsgTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
import re
import time
from langchain_core.runnables import RunnableConfig
from langchain_community.tools import DuckDuckGoSearchRun

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

def init_chat():
    if "history" not in st.session_state:
        st.session_state.history = []
    history = StreamlitChatMessageHistory()
    st.session_state.steps = {}
    avatars = {"human": "user", "ai": "assistant"}
    memory = ConversationBufferMemory(chat_memory=history, return_messages=True, memory_key="chat_history", output_key="output")
    for idx, message in enumerate(history.messages):       
        with st.chat_message(avatars[message.type]):
            for step in st.session_state.steps.get(str(idx), []):
                if step[0].tool == "_Exception":
                    continue
                with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                    st.write(step[0].log)
                    st.write(step[1])
            st.write(message.content)

    if msg := st.chat_input(placeholder="무엇이든 물어보세요"):
        st.chat_message("user").write(msg)
        st.session_state.history.append({"role": "user", "content": msg})
        with st.chat_message("assistant"):
            cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            cfg = RunnableConfig()
            cfg["callbacks"] = [cb]
            executor = init_agent_chain(memory)
            res = executor.invoke(msg, cfg)
            st.write_stream(chat_stream(res["output"]))
            st.session_state.steps[str(len(history.messages) - 1)] = res["intermediate_steps"]

def init_agent_chain(memory):
    llm = ChatOpenAI(model_name  = os.environ['OPENAI_API_MODEL'], temperature = os.environ['OPENAI_API_TEMPERATURE'], streaming = True)
    tools = [DuckDuckGoSearchRun(name="Search")]
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    return AgentExecutor.from_agent_and_tools(agent=chat_agent, tools=tools, memory=memory, return_intermediate_steps=True, handle_parsing_errors=True)

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