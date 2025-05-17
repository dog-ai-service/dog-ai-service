# ui
import streamlit as st
# 히스토리- 단기기억 재현 - 대화 내용 유지
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# 랭체인 + openai 관련 로드
from langchain_openai import ChatOpenAI
# Gpt에게 전달할 사용자 메세지 포맷 로드
from langchain.schema import HumanMessage
# 설정 : ai 설정값 가져오기
from services.login_api import ai_res_type

from agents.init_agent import init_agent_chain
from langchain.callbacks import StreamlitCallbackHandler


#질문창
def prompt_box():
    prompt = st.chat_input('무엇이 궁금한가요?')
    print(prompt)
    # 히스토리 처리 -> 기억 -> 랭체인(단기기억) or 백터디비(장기기억)
    history = StreamlitChatMessageHistory()
    # 대화 내역 출력 -> 반복
    for message in history.messages:
        # 메세지 유형( 사용자 혹은 ai(어시스턴스) ) + 메세지 형태
        st.chat_message(message.type).write(message.content)

    # 채팅(봇) 창에 메세지 세팅
    # prompt가 존재하면
    if prompt:  # 뭔가를 입력했다
        with st.chat_message('user'):  # 일반 유저의 아이콘으로 채팅창에 메세지 세팅되는 표식
            # 히스토리에 사용자 메세지(프럼프트) 저장
            history.add_user_message(prompt)
            # 사용자 메세지를 표기
            st.markdown(prompt)

        with st.chat_message('assistant'):
            # ai의 응답 ; openai | openai + 위키피디아 +  기타 검색엔진등 증강하여
            if ai_res_type == 2:    # openai + 위키피디아 +  기타 검색엔진등 증강하여 답변
                # 1. 콜백 구성
                cb = StreamlitCallbackHandler(st.container())
                # 2. 랭체인 에이전트 구성 -> 히스토리 전달 -> 대화 내용을 전달(기억)
                agent_chain = init_agent_chain(history)
                # 3. 에이전트 이용하여 llm 질의
                res = agent_chain.invoke(
                    {"input": prompt},   # 사용자의 질의
                    {"callbacks": [cb]}  # 응답 작성중에 로그->화면 표기등등 연출
                )
                # 4. 응답 -> 히스토리 등록
                history.add_ai_message(res['output'])
                # 5. 결과 출력
                st.markdown(res['output'])
                pass
            elif ai_res_type == 1:  # openai로만 답변
                # 1. GPT 처리할수 있는 ChatOpenAI 객체 생성
                llm = ChatOpenAI(
                    model_name=os.environ['OPENAI_API_MODEL'],
                    temperature=os.environ['OPENAI_API_TEMPERATURE']
                )
                # 2. 프럼프트 엔지니어링 (서비스 컨셉 부여 가능) 여기서는 휴먼메세지구성
                msg = [HumanMessage(content=prompt)]
                # 4. GPT 요청 -> 콜백 처리 함수는 다름(에이전트에서 처리)
                res = llm.invoke(msg)
                # 5. 응답 도착, 히스토리에 담기
                print(res.content)
                history.add_ai_message(res.content)
                # 6. 화면 세팅
                st.markdown(res.content)
                pass
            else:  # 더미 응답
                st.markdown('안녕하세요! 무엇을 도와드릴까요? 😊')