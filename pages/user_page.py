from services.login_api import login_api
# ui
import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar
from components.dog_ui import dog_info_page
import jwt
sidebar()

if "token" not in st.session_state:
    st.title("로그인 해주세요")
else:
    token = st.session_state.token
    id_token = token["token"]["id_token"]
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    st.title(f"{decoded['name']}님의 강아지 정보")
    st.markdown('---')
    # 각 강아지 카드
    dog_info_page()