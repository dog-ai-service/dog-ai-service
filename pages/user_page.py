from services.login_api import login_api
# ui
import streamlit as st
#사이드바 로그인
from components.sidebar import sidebar
import jwt
sidebar()
# 더미데이터
dogs = [
    {
        "name": "몽이",
        "gender": "M",
        "age": 3,
        "weight": 5.2,
        "note": "슬개골 탈구, 식욕이 과함",
        "img": "https://www.dailysecu.com/news/photo/202104/123449_145665_1147.png"  # 실제 이미지 URL 또는 로컬 경로
    },
    {
        "name": "삐삐",
        "gender": "F",
        "age": 6,
        "weight": 3.8,
        "note": "간식을 급하게 먹고 자주 구토, 얼음 먹는걸 좋아함, 분리불안 증세",
        "img": "https://images.mypetlife.co.kr/content/uploads/2021/10/19151330/corgi-g1a1774f95_1280-1024x682.jpg"
    }
]
genders = {"M":"♂️", "F":"♀️"}

if "token" not in st.session_state:
    st.title("로그인 해주세요")
else:
    token = st.session_state.token
    id_token = token["token"]["id_token"]
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    st.title(f"{decoded['name']}님의 강아지 정보")
    st.markdown('---')
    # 각 강아지 카드
    for idx, d in enumerate(dogs):
        cols = st.columns([1, 5, 1])  # [이미지, 내용, 버튼]
        with cols[0]:
            st.image(d["img"], width=200)
        with cols[1]:
            # 이름·성별·나이·무게
            st.markdown(
                f"### {d['name']} {genders[d['gender']]}   {d['age']}살   {d['weight']}kg"
            )
            st.write(d["note"])
        with cols[2]:
            if st.button("수정", key=f"edit_{idx}"):
                st.success(f"{d['name']} 정보 수정 페이지로 이동")  # 실제 수정 페이지 연결

        st.markdown("---")  # 구분선

    # + 버튼 중앙 배치
    btn_cols = st.columns([3, 1, 3])
    with btn_cols[1]:
        if st.button("➕", use_container_width=True):
            st.info("새 강아지 등록 모달 열기")  # 실제 등록 로직 연결