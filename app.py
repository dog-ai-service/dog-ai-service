'''
    메인 페이지
'''

import streamlit as st
from dotenv import load_dotenv
from make_calendar import init_calendar
from sidebar import sidebar
from create_schedule import create_schedule



load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

st.set_page_config(page_title="AI Calendar for Dogs", page_icon="📆")

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False



# 메인 앱 실행
def main():
    # if st.session_state.page == "login" and not st.session_state.logged_in:
    #     login()
    # elif st.session_state.page == "signup":
    #     signup()
    # elif st.session_state.logged_in:
    #     init_calendar()
    #     sidebar()
    #     chatbot()
    

    # 일단 로그인은 되었다고 가정하고 바로 메인화면
    init_calendar()
    sidebar()
    # summation_button 우측 하단에 배치
    create_schedule()
    




if __name__ == "__main__":
    main()
