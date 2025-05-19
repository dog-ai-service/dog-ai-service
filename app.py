# 모듈가져오기
# ui
import streamlit as st
# 컴포넌트
from components.sidebar import sidebar

def init_chat():
    sidebar()
    
def main():
    init_chat()

# 프로그램 가동
if __name__ == '__main__':
    main()