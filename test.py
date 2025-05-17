import streamlit as st

def sidebar():
    st.sidebar.title("메뉴")
    choice = st.sidebar.radio("메뉴 선택", ["홈", "정보", "설정"])
    return choice

def home():
    st.title("홈")
    st.write("여기는 홈 화면입니다.")

def info():
    st.title("정보")
    st.write("서비스 정보 페이지")

def settings():
    st.title("설정")
    st.write("설정 페이지")

def main():
    page = sidebar()
    
    if page == "홈":
        home()
    elif page == "정보":
        info()
    elif page == "설정":
        settings()

if __name__ == "__main__":
    main()