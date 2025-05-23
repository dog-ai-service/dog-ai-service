# ui
import streamlit as st
# 로그인
from streamlit_oauth import OAuth2Component
# 로그인 토큰 해석
import jwt
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from config import REDIRECT_URI
from services.drive_api import read_json_list_by_name, upload_json_list_to_drive, _convert_dates
import time
import json

# 설정 : 1. openai만 사용, 2. 랭체인 에이전트를 이용 검색증강, 3. 더미
ai_res_type = 2

def get_created_events_json():
    """
    st.session_state.created_events (dict) 를
    list of dict 형태의 JSON 문자열로 반환합니다.
    """
    ce = st.session_state.get('created_events', {})
    # JSON 파일로 저장할 때 list 구조로 감싸기
    json_list = [ce]
    return json.dumps(json_list, ensure_ascii=False, indent=2)

def login_api():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

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
            name="Google로 시작하기\n클릭",
            icon="",
            redirect_uri=REDIRECT_URI, # 여기 나중에 로컬 아닌 버전으로 수정해야함
            scope="openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets"
        )
        if token:
            st.session_state.token = token  # 세션에 저장
            st.rerun()  # 새로고침해서 버튼 숨김
    else:
        token = st.session_state.token
        id_token = token["token"]["id_token"]
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        st.success(f"✅ {decoded['name']}님 로그인됨")
        st.image(decoded['picture'], width=100)
        st.write(f"이메일: {decoded['email']}")
        # 3) 최초 로그인 시점에만 Drive에서 데이터 불러오기
        if not st.session_state.get("initialized", False):
            st.session_state.dogs = read_json_list_by_name(folder_name="dog_ai_service", filename="dogs_info.json")
            st.session_state.schedules = read_json_list_by_name(folder_name="dog_ai_service", filename="schedules.json")
            st.session_state.chat_history = read_json_list_by_name(folder_name="dog_ai_service", filename="chat_history.json")
            st.session_state.created_events = read_json_list_by_name(folder_name="dog_ai_service", filename="created_events.json")
            st.session_state.symptom_chat_history = read_json_list_by_name(folder_name="dog_ai_service", filename="symptom_chat_history.json")
            st.session_state.initialized = True
            st.success("✅ Drive 동기화 완료")
        
        if st.button("로그아웃"):
            upload_json_list_to_drive(_convert_dates(st.session_state.get("dogs", [])), "dogs_info.json")
            upload_json_list_to_drive(_convert_dates(st.session_state.get("schedules", [])), "schedules.json")
            upload_json_list_to_drive(_convert_dates(st.session_state.get("chat_history", [])), "chat_history.json")
            upload_json_list_to_drive(_convert_dates(st.session_state.get("created_events", [])), "created_events.json")
            upload_json_list_to_drive(_convert_dates(st.session_state.get("symptom_chat_history", [])), "symptom_chat_history.json")
            # 세션 상태 비우기
            for key in ["dogs", "schedules", "created_events", "initialized", "token", "chat_history", "created_events", "symptom_chat_history"]:
                st.session_state.pop(key, None)
            st.success("✅ 로그아웃 완료")
            time.sleep(1)
            st.rerun()
        # if st.button("구글드라이브 연동 확인"):
        #     print("강아지 데이터 확인 : ", st.session_state.dogs)
        #     print("스케줄 데이터 확인 : ", st.session_state.schedules)
        #     print("캘린더 데이터 확인 : ", st.session_state.created_events)
        #     print("대화내역 확인     : ", st.session_state.chat_history)
        #     print("증상 대화내역 확인 : ", st.session_state.symptom_chat_history)