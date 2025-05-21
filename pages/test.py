import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import json
from services.drive_api import upload_json_list_to_drive, read_json_list_by_name
from components.sidebar import sidebar



sidebar()

dogs = [
    {"이름": "뽀삐", "나이": "3", "몸무게": "5.2"},
    {"이름": "초코", "나이": "5", "몸무게": "9.1"},

]

if st.button("📁 강아지 리스트 JSON 파일로 Drive에 저장하기"):
    upload_json_list_to_drive(dogs, filename="강아지리스트.json")
    #sheet_create()
    #create_folder()
if st.button("📁 강아지 리스트 JSON 파일 읽어오기"):
    st.info(f"강아지 정보들 {read_json_list_by_name()}")


