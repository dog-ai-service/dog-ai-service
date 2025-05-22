# ui
import streamlit as st
# 로그인
from streamlit_oauth import OAuth2Component
# 로그인 토큰 해석
import jwt
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, COOKIE_SECRET

# 설정 : 1. openai만 사용, 2. 랭체인 에이전트를 이용 검색증강, 3. 더미
ai_res_type = 2

GOOGLE_CLIENT_ID="너 클라아이디"
GOOGLE_CLIENT_SECRET="너 클라 비번"

def login_api():
    client_id=GOOGLE_CLIENT_ID#너 클라이언트 아이디 넣어
    client_secret=GOOGLE_CLIENT_SECRET#너 클라이언트 비번 넣어

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
            redirect_uri="http://localhost:8080", # 여기 나중에 로컬 아닌 버전으로 수정해야함
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
        if st.button("로그아웃"):
            del st.session_state["token"]
            st.rerun()

