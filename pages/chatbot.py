'''
    챗봇 페이지 코드
        - ai_res_type으로 일반 챗봇과 증상 챗봇을 구분함.
'''
import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor, load_tools, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.callbacks.base import CallbackManager
#사이드바 로그인
from components.sidebar import sidebar


load_dotenv()
ai_res_type = 0

st.title("💬 강아지 증상 전문 챗봇")

# 토글버튼을 통해 증상 챗봇 활성화/비활성화 -> 활성화면 ai_res_type = 1, 비활성화면 ai_res_type = 0
# 최대한 오른쪽에 배치
st.toggle("증상 챗봇 활성화", value=False, key="symptom_chatbot")
if st.session_state.symptom_chatbot:
    ai_res_type = 1

def chatbot():
    # 히스토리 관리 객체 생성
    history = StreamlitChatMessageHistory()

    # 이전 대화 내용 렌더링
    for message in history.messages:
        st.chat_message(message.type).write(message.content)

    # 사용자 입력
    prompt = st.chat_input('무엇이 궁금한가요?')
    if prompt:
        st.session_state.symptom_prompt = prompt
        # 사용자 입력 출력 및 히스토리에 추가
        with st.chat_message('user'):
            st.markdown(prompt)
            history.add_user_message(prompt)

        # 질의 가공
        formatted_prompt = f'''
        {prompt}
        의심되는 증상명 3가지 알려줘. 
        또한, 각 증상명에 대한 증상설명을 해줘.
        아래 형식과 같이 응답을 줘.

        < 예시 >
        1. 증상명 - 증상설명  
        2. 증상명 - 증상설명  
        3. 증상명 - 증상설명  
        '''
        
        # LlamaIndex 쿼리 수행
        s_context = StorageContext.from_defaults(persist_dir='index_db_backup')
        loaded_index = load_index_from_storage(s_context)
        loaded_query_engine = loaded_index.as_query_engine()
        response = loaded_query_engine.query(formatted_prompt)

        # 응답 출력 및 히스토리에 추가
        with st.chat_message('assistant'):
            st.markdown(response.response)
            history.add_ai_message(response.response)


def init_chat():
    prompt = st.chat_input('무엇이 궁금한가요?')
    history = StreamlitChatMessageHistory()
    for message in history.messages:
        st.chat_message(message.type).write(message.content)

    if prompt:  
        with st.chat_message('user'):  
            history.add_user_message(prompt)
            st.markdown(prompt)

        with st.chat_message('assistant'):
            cb = StreamlitCallbackHandler(st.container())
            agent_chain = init_agent_chain(history)
            res = agent_chain.invoke(
                {"input": prompt},   
                {"callbacks": [cb]}  
            )
            history.add_ai_message(res['output'])
            st.markdown(res['output'])
            pass



def init_agent_chain(history):
    llm = ChatOpenAI(
        model_name=os.environ['OPENAI_API_MODEL'],
        temperature=os.environ['OPENAI_API_TEMPERATURE']
    )
    tools = load_tools(["wikipedia"])
    hub_tool = hub.pull('hwchase17/openai-tools-agent')
    memory = ConversationBufferMemory(
        chat_memory=history,
        memory_key='my_first_chat',
        return_messages=True
    )
    agent = create_openai_tools_agent(llm, tools, hub_tool)
    return AgentExecutor(agent=agent, tools=tools, memory=memory)



sidebar()
if ai_res_type == 1:
    chatbot()
else:
    init_chat()
