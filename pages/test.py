# ui
import streamlit as st
# 사이드바 로그인
from components.sidebar import sidebar
#
from services.drive_api import sheet_create, sheet_write

sidebar()
sheet=None
if st.button("생성버튼"):
    st.write("생성중")
    st.session_state.sheet=sheet_create()

dogs = [
    {
        "이름": "뽀삐",
        "나이": "3",
        "몸무게": "5.2",
        "견종": "말티즈",
        "성별": "암컷",
        "예방접종": "O",
        "중성화": "X",
        "특이사항": "알레르기 있음"
    },
    {
        "이름": "초코",
        "나이": "5",
        "몸무게": "8.1",
        "견종": "시바견",
        "성별": "수컷",
        "예방접종": "X",
        "중성화": "O",
        "특이사항": "사람을 좋아함"
    }
]

if st.button("정보추가"):
    st.write(sheet)
    if "sheet" not in st.session_state:
        st.write("생성 버튼을 먼저 누르세요")
    else:
        st.write("정보추가중")
        sheet_write(
            spreadsheet_id=st.session_state.get("sheet","미기입"),
            dogs=dogs,
            )
        

