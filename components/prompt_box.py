# ui
import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from services.login_api import ai_res_type
from agents.init_agent import init_agent_chain
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableConfig
import time


def chat_stream(response):
    for char in response:
        yield char
        time.sleep(0.02)

#질문창
def prompt_box():
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
        with st.chat_message("assistant"):
            cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            cfg = RunnableConfig()
            cfg["callbacks"] = [cb]
            executor = init_agent_chain(memory)
            res = executor.invoke(msg, cfg)
            st.write_stream(chat_stream(res["output"]))
            st.session_state.steps[str(len(history.messages) - 1)] = res["intermediate_steps"]