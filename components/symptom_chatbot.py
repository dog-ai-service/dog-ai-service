import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from llama_index.core import StorageContext, load_index_from_storage
# 번역 라이브러리
from deep_translator import GoogleTranslator
import re
from services.AI.make_health_note import make_health_note
from services.drive_healthnote_api import *



def symptom_chatbot():
    # 히스토리 관리 객체 생성
    history = StreamlitChatMessageHistory()

    # 이전 대화 내용 렌더링
    for message in history.messages:
        st.chat_message(message.type).write(message.content)

    # 사용자 입력
    prompt = st.chat_input('강아지의 증상을 자세히 입력할수록 더 정확한 답변을 받을 수 있어요.')
    if prompt:
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
        And explain how to deal with each symptom.

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
            ko_response = f"""### 🩺 예측해볼 수 있는 질병들
{ko_response}

> #### 🔎 자세한 상담은 반드시 수의사와 진행하시길 바랍니다.
            """

        
        # 응답 출력 및 히스토리에 추가
        with st.chat_message('assistant'):
            st.markdown(ko_response)
            history.add_ai_message(ko_response)
        
        with st.spinner("강아지 건강 정보를 기입중입니다..."):
            # 강아지 증상 정보를 가져오는 코드
            try:
                health_info = make_health_note(prompt)
                # 이름 뽑아오기 성공 -> health_note의 인자로 넘겨야함.
                names = re.findall(r"\d+\.\s*([^:]+?)\s*:", ko_response, flags=re.DOTALL)
                health_info['의심 질병'] = ", ".join(names)
                res = sheet_write(get_sheet_id(), [health_info])
                if res is not None:
                    st.success("기입 완료!")

            except:
                health_info = {'날짜': '', '주요 증상': '', '의심 질병': '', '필요한 조치': '', '추가 메모': ''}
                res = sheet_write(get_sheet_id(), [health_info])
                if res is not None:
                    st.success("기입 완료!")
    

            