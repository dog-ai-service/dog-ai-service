# ui
import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from services.login_api import ai_res_type
from agents.init_agent import init_agent_chain
from langchain.callbacks import StreamlitCallbackHandler as LCHandler
from langchain_community.callbacks import StreamlitCallbackHandler as CCHandler
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableConfig
import time


def chat_stream(response):
    for char in response:
        yield char
        time.sleep(0.02)

#질문창
def prompt_box():
    # 1) 세션에 로드된 chat_history를 먼저 렌더링
    if "steps" not in st.session_state:
        st.session_state.steps = {}
    if "chat_history" in st.session_state:
        for msg in st.session_state.chat_history:
            role = msg.get("role", "user")
            with st.chat_message("user" if role=="user" else "assistant"):
                st.write(msg.get("content", ""))
    else:
        st.session_state.chat_history = []

    # 2) 새 메시지를 입력받으면
    if user_msg := st.chat_input(placeholder="무엇이든 물어보세요"):
        # (1) 사용자 메시지 저장 & 렌더링
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        st.chat_message("user").write(user_msg)

        # (2) 에이전트 호출
        memory = ConversationBufferMemory(
            chat_memory=StreamlitChatMessageHistory(), 
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )
        executor = init_agent_chain(memory)
        with st.chat_message("assistant"):
            cb = CCHandler(st.container(), expand_new_thoughts=False)
            cfg = RunnableConfig(callbacks=[cb])
            res = executor.invoke(user_msg, cfg)
            # 스트리밍 출력
            assistant_output = "".join(chat_stream(res["output"]))
            st.write(assistant_output)

        # (3) AI 응답 저장
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_output})
        # steps 기록
        st.session_state.steps[str(len(st.session_state.chat_history) - 1)] = res["intermediate_steps"]