# 모듈가져오기
# ui
import streamlit as st
# 컴포넌트
from components.sidebar import sidebar
# streamlit 캘린더 ui
from components.st_calendar import st_calendar
# 일정 생성 및 일정 요약
from components.create_schedule import create_schedule


    
def main():
    sidebar()
    st_calendar()
    create_schedule()

# 프로그램 가동
if __name__ == '__main__':
    main()


