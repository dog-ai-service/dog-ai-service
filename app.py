# 모듈가져오기
# ui
import streamlit as st
# 컴포넌트
from components.sidebar import sidebar
# 서비스
from pages import calendar_page, chatbot_page, login_page


def init_chat():
    page = sidebar()
    
    if page == "캘린더":
        calendar_page()
    elif page == "챗봇":
        chatbot_page()
    #elif page == "사용자 정보":
    #    login_page()
    
    

def main():
    init_chat()

# 프로그램 가동
if __name__ == '__main__':
    main()