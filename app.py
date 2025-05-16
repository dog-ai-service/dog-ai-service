'''
    서비스 설명
        - 단기기억 사용(대화 내용 메모리) -> GPT 응답 처리 가능하게 구성
'''
# 모듈가져오기
# ui
import streamlit as st
# 환경변수 로드
from dotenv import load_dotenv
import os
# 랭체인 + openai 관련 로드
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
# 히스토리- 단기기억 재현 - 대화 내용 유지
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# 답변을 구성하는 과정을 콜백함수로 계속 제공받아서 -> 화면상에 인터렉티브한 변화를 연출
from langchain_community.callbacks import StreamlitCallbackHandler
# 랭체인 에이전트
# AgentExecutor : 에이전트, 툴, 메모리 모두 결합
# load_tools : 위키피디아, 검색엔등등 연결
# create_openai_tools_agent : openai를 위한 에이전트 (메모리, 툴, 모델)
from langchain.agents import AgentExecutor, load_tools, create_openai_tools_agent
# 대화 내용을 기반으로 gpt가 응답을 할수 있게 제공
from langchain.memory import ConversationBufferMemory
# 허브
from langchain import hub
# 로그인
from streamlit_oauth import OAuth2Component
# 로그인 토큰 해석
import jwt
# 구글 캘린더 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime


# 환경변수 파일 로드 -> 데이터 획득
load_dotenv()
# 확인
# print(os.environ['OPENAI_API_KEY'])
# print(os.environ['OPENAI_API_MODEL'])
# print(os.environ['OPENAI_API_TEMPERATURE'])

# 설정 : 1. openai만 사용, 2. 랭체인 에이전트를 이용 검색증강, 3. 더미
ai_res_type = 2

# ui 함수 모음
#사이드바
def sidebar():
    st.sidebar.title('this is sidebar')
    st.sidebar.checkbox('체크박스에 표시될 문구')
    return

#로그인
def login_api():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    oauth2 = OAuth2Component(
        client_id=client_id,
        client_secret=client_secret,
        authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
    )

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        token = oauth2.authorize_button(
            name="Continue with Google",
            icon="",
            redirect_uri="http://localhost:8080",
            scope = "openid email profile https://www.googleapis.com/auth/calendar" # 구글 캘린더에서 읽고 쓰기 가능
        )

        if token:
            st.session_state.token = token  # 세션에 저장
            st.rerun()  # 새로고침해서 버튼 숨김
        

    else:
        token = st.session_state.token
        st.success("✅ 로그인 성공!")
        id_token = token["token"]["id_token"]
        decoded = jwt.decode(id_token, options={"verify_signature": False})
        
        st.write(f"환영합니다, {decoded['name']}님")
        st.image(decoded['picture'], width=100)
        st.write(f"이메일: {decoded['email']}")

        if token:
            creds = Credentials(
                token=token["token"]["access_token"],
                refresh_token=token.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=[
                    "https://www.googleapis.com/auth/calendar.readonly"
                ]
            )

            # 캘린더 API 서비스 객체 생성
            service = build("calendar", "v3", credentials=creds)

            # 오늘 일정 가져오기
            import datetime
            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])

            st.subheader("📅 오늘 이후 이벤트")
            if not events:
                st.write("예정된 일정이 없습니다.")
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                st.write(f"- {start}: {event['summary']}")



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





# 전역 변수 파트


def init_chat():
    '''
        채팅 초기화 - UI, 채팅 메세지 히스토리 처리, 프럼프트처리
    '''
    # 제목
    st.title('LLM,랭체인,streamlit기반 서비스')
    # sidebar
    sidebar()
    # 로그인
    login_api()
    # 채팅 입력창
    # 로그인한 사용자만 아래 실행
    if "token" in st.session_state:
        prompt_box()
    pass

# 랭체인-에이전트 초기화


def init_agent_chain(history):
    '''
        - 여러 개의 작업을 연속적으로 연결(chain)되어서 진행되게 구성 -> 주체:agent
        - parameters
            - history : 대화 내역
        - returns
            - AgentExecutor 객체        
    '''
    # 1. GPT 생성
    llm = ChatOpenAI(
        model_name=os.environ['OPENAI_API_MODEL'],
        temperature=os.environ['OPENAI_API_TEMPERATURE']
    )
    # 2. 툴 생성 (hub를 통해서 외부 자원 활용 -> 검색증강, 데이터 추가 등등....)
    tools = load_tools([  # "ddg-search",
        "wikipedia"])
    # 3. 외부 자원을 사용하루 있는 허브 구성
    hub_tool = hub.pull('hwchase17/openai-tools-agent')
    # 4. (*)메모리 구성 (채팅 대화 기록을 기반으로 응답할수 있게 구성)
    memory = ConversationBufferMemory(
        chat_memory=history,
        # 이 대화에 대해 특정할수 있는 키, 현재는 고정, 차후 대화별로 다르게 구성 가능함
        # chatgpt 에서 왼쪽 메뉴에 대화창 별로 관리되는 항목 체크
        memory_key='my_first_chat',
        return_messages=True
    )
    # 5. 에이전트 구성 (모델, 툴, 허브) : openai + 외부자원
    agent = create_openai_tools_agent(llm, tools, hub_tool)
    # 6. (*)에이전트 실행자 구성 (에이전트, 툴, 메모리) => 에이전트 체인
    return AgentExecutor(agent=agent, tools=tools, memory=memory)


def main():
    '''
        메인 함수 - 프로그램 엔트리 포인트(진입로)
    '''
    init_chat()
    pass


# 프로그램 가동
if __name__ == '__main__':
    main()
