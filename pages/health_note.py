import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar

from services.drive_healthnote_api import *
#pdf관련
from services.make_pdf_data_api import make_pdf_data


sidebar()
st.title("🐶 강아지 헬스 노트 자동 작성기")

# sheet에 있는 정보 불러오기 --> values는 json형식
values = sheet_read(get_sheet_id())

# 강아지 이름은 견주에 맞춰서 동적 생성 --> 사용자 정보에서 받아오게 연결 (추후)
dog_name = "푸딩이"

try:
    if len(values) != 0:
        if st.button('요약 생성하기'):
            with st.spinner("요약 PDF 생성중입니다..."):
                # 다운로드 버튼 표시
                st.download_button(
                    label="📄 건강정보 요약 PDF 다운로드",
                    file_name=f"{dog_name}_헬스노트.pdf",
                    data=make_pdf_data(values), # 바이너리 데이터 들어가야함.
                    mime="application/pdf"
                )
    else:
        st.info("강아지의 증상을 증상 챗봇에 입력하면 자동으로 기입됩니다!")
except:
    pass



