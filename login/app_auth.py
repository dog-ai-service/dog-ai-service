'''
    로그인 페이지
        - 현재는 사용 X
'''


import streamlit as st
from datetime import date

# 로그인 화면
def login():
    st.title("AI Calendar for Dogs - 로그인")
    with st.form("login_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

    if submitted:
        if email == "" and password == "":
            st.success("로그인 성공!")
            st.session_state.logged_in = True
            st.session_state.page = "calendar"
        else:
            st.error("로그인 실패. 이메일과 비밀번호를 확인하세요.")

    if st.button("회원가입"):  # 회원가입으로 이동
        st.session_state.page = "signup"

# 회원가입 화면 + 강아지 정보 입력

def signup():
    st.title("AI Calendar for Dogs - 회원가입")
    with st.form("signup_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        dog_name = st.text_input("강아지 이름")
        birthday = st.date_input("생일", value=date.today())
        vaccination_date = st.date_input("예방접종 날짜", value=date.today())
        submitted = st.form_submit_button("회원가입 완료")

    if submitted:
        if email == "" and password == "":
            st.success("회원가입 성공! 로그인해주세요.")
            st.session_state.page = "login"
        else:
            st.error("회원가입 실패. 이메일과 비밀번호를 확인하세요.")

    if st.button("로그인으로 돌아가기"):
        st.session_state.page = "login"