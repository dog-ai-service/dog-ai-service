'''
    사이드 바 
'''


import streamlit as st


# 캘린더 창 (메인 페이지)에서 사이드바 추가
def sidebar():
    st.sidebar.title("🐶 환영합니다, 견주님!")


    # 로그아웃 버튼은 하단에 따로 배치
    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "login"