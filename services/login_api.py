# ui
import streamlit as st
# 로그인
from streamlit_oauth import OAuth2Component
# 로그인 토큰 해석
import jwt
# 구글 캘린더 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# 설정 : 1. openai만 사용, 2. 랭체인 에이전트를 이용 검색증강, 3. 더미
ai_res_type = 2

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
            name="Continue with Google",
            icon="",
            redirect_uri="http://localhost:8080",
            scope="openid email profile https://www.googleapis.com/auth/calendar"
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

        # 캘린더에 사용을 위한 구글계정 정보를 세션에서 가져오기
        creds = Credentials(
            token=token["token"]["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        # 캘린더 API 서비스 객체 생성
        service = build("calendar", "v3", credentials=creds)
        # 오늘 일정 가져오기
        now = datetime.datetime.utcnow().isoformat() + "Z"
        # 캘린더에서 대충 최신 이벤트 5개 가져오기
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
