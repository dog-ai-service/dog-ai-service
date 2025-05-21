import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import json
# 암호화 비밀번호 (실제 서비스에선 환경변수로 관리하세요)
COOKIE_SECRET = "my-very-secret-key"

cookies = EncryptedCookieManager(
    prefix="myapp/",
    password=COOKIE_SECRET,
)

if not cookies.ready():
    st.stop()

st.title("EncryptedCookieManager 테스트")

token = cookies.get("token", None)

if token:
    st.write("쿠키에 저장된 토큰:", token)
else:
    st.write("쿠키에 토큰이 없습니다.")

if st.button("쿠키에 토큰 저장"):
    sample_token = {"access_token": "abc123", "expires_in": 3600}
    cookies["token"] = json.dumps(token)
    st.rerun()

if st.button("쿠키에서 토큰 삭제"):
    if "token" in cookies:
        del cookies["token"]
    st.rerun()
