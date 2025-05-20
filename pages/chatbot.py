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
# 번역 라이브러리
from deep_translator import GoogleTranslator
import re


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
    prompt = st.chat_input('강아지의 증상을 자세히 입력할수록 더 정확한 답변을 받을 수 있어요.')
    if prompt:
        st.session_state.symptom_prompt = prompt
        # 사용자 입력 출력 및 히스토리에 추가
        with st.chat_message('user'):
            st.markdown(prompt)
            history.add_user_message(prompt)

        
        # 질의 가공
        # 1. prompt 영어로 번역
        translated_prompt = GoogleTranslator(source="auto", target="en").translate(prompt)
        # 2. 프롬프트 가공 
        formatted_prompt = f'''
        {translated_prompt}
        Tell me three suspected symptoms.
        Also, explain each symptom in detail.
        Please respond in the format below.

        <Example>
        1 . Heart disease: Heart disease is a common cardiac valve disease in dogs that can lead to issues like gasping, lack of energy, and coughing. It is important to conduct regular heart tests to prevent this condition.
        '''
        with st.spinner("AI가 질병을 분석하고 있어요..."):
        # LlamaIndex 쿼리 수행
            s_context = StorageContext.from_defaults(persist_dir='index_db_backup')
            loaded_index = load_index_from_storage(s_context)
            loaded_query_engine = loaded_index.as_query_engine()
            en_response = loaded_query_engine.query(formatted_prompt)
            text = en_response.response
            items = re.findall(r"\d+\..*?(?=\n\d+\.|\Z)", text, flags=re.DOTALL)
            translated = []
            for i, item in enumerate(items, 1):
                ko = GoogleTranslator(source='en', target='ko').translate(item.strip())
                translated.append(f"{ko}")
            ko_response = "\n\n".join(translated)
            print(ko_response)
            ko_response = f"""### 🩺 예측해볼 수 있는 질병들
{ko_response}

> #### 🔎 자세한 상담은 반드시 수의사와 진행하시길 바랍니다.
            """

        
        # 응답 출력 및 히스토리에 추가
        with st.chat_message('assistant'):
            st.markdown(ko_response)
            history.add_ai_message(ko_response)


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
