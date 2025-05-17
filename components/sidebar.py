# ui
import streamlit as st

#사이드바
def sidebar():
    st.sidebar.title('this is sidebar')
    st.sidebar.checkbox('체크박스에 표시될 문구')
    return