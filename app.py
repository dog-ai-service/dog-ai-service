# 모듈가져오기
# ui
import streamlit as st
# 컴포넌트
from components.sidebar import sidebar
from components.prompt_box import prompt_box
# 서비스
from services.login_api import login_api

def init_chat():

    page = sidebar()
    
    if page == "캘린더":
        # 제목
        st.title("캘린더 넣을 예정")
    elif page == "챗봇":
        # 채팅 입력창
        # 로그인한 사용자만 아래 실행
        if "token" in st.session_state:
            #프롬프트
            prompt_box()
        else :
            st.title("사용자 정보에서 로그인하세요")
    elif page == "사용자 정보":
        login_api()

    # 로그인
    
    

def main():
    init_chat()

# 프로그램 가동
if __name__ == '__main__':
    main()