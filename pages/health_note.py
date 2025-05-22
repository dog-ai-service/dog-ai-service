import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar

from services.drive_healthnote_api import *
#pdf관련
from services.make_pdf_data_api import make_pdf_data


sidebar()
st.title("🐶 강아지 헬스 노트 자동 작성기")

names = []
values = {}
try:
    for item in st.session_state.dogs:
        values[item['name']] = sheet_read(get_sheet_id(item['name']), item['name'])
        names.append(item['name'])
except:
    st.info("강아지의 증상을 증상 챗봇에 입력하면 자동으로 기입됩니다!")
# sheet에 있는 정보 불러오기 --> values는 json형식
# values = sheet_read(get_sheet_id())


name = st.selectbox(
     '어떤 강아지의 정보를 요약해드릴까요?',
     names,
     index=None,
     placeholder="선택해주세요",
)

try:
    if name:
        if st.button('요약 생성하기'):
            with st.spinner("요약 PDF 생성중입니다..."):
                # 다운로드 버튼 표시
                st.download_button(
                    label="📄 건강정보 요약 PDF 다운로드",
                    file_name=f"{name}_헬스노트.pdf",
                    data=make_pdf_data(values[name]), # 바이너리 데이터 들어가야함.
                    mime="application/pdf"
                )
except:
    pass



