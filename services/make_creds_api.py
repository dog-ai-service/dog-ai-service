

# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


# 
def make_creds(scope):
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        pass
    else:
        token = st.session_state.token
        # 드라이브(스프레드시트) 사용을 위한 구글계정 정보를 세션에서 가져오기
        creds = Credentials(
            token=token["token"]["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[f"https://www.googleapis.com/auth/{scope}"]
        )


        return creds