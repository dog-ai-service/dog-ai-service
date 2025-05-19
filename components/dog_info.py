import streamlit as st

# 더미데이터
if "dogs" not in st.session_state:
    st.session_state.dogs = [
        {
            "name": "몽이",
            "gender": "수컷",
            "age": 3,
            "weight": 5.2,
            "note": "슬개골 탈구, 식욕이 과함",
            "breed": "포메라니안", 
            "feed_period": "", 
            "feed_time": "",
            "walk_period": "",
            "walk_time": "",
            "vaccination_period": "",
            "vaccination_time": "",
            "bath_period": "",
            "bath_time": "",
            "anthelmintic_period": "",
            "anthelmintic_time": "",

        },
        {
            "name": "삐삐",
            "gender": "암컷",
            "age": 6,
            "weight": 3.8,
            "note": "간식을 급하게 먹고 자주 구토, 얼음 먹는걸 좋아함, 분리불안 증세", 
            "breed": "웰시코기",
            "feed_period": "", 
            "feed_time": "",
            "walk_period": "",
            "walk_time": "",
            "vaccination_period": "",
            "vaccination_time": "",
            "bath_period": "",
            "bath_time": "",
            "anthelmintic_period": "",
            "anthelmintic_time": "",
        }
    ]
# 강아지 성별 아이콘
genders = {"수컷":"♂️", "암컷":"♀️"}
# 강아지 견종 이미지
dog_imgs = {"포메라니안":"https://www.dailysecu.com/news/photo/202104/123449_145665_1147.png", 
           "웰시코기":"https://images.mypetlife.co.kr/content/uploads/2021/10/19151330/corgi-g1a1774f95_1280-1024x682.jpg"}

if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None

def dog_info():
    # 각 강아지 카드
    for idx, dog in enumerate(st.session_state.dogs):
        cols = st.columns([1, 5, 1])
        if dog["breed"] in dog_imgs:
            img = dog_imgs[dog["breed"]]
        else: # 강아지 견종의 이미지 데이터 없을 경우
            img = "https://cdn-icons-png.flaticon.com/512/608/608502.png"
        with cols[0]:
            st.image(img, width=200)
        with cols[1]:
            st.markdown(f"### {dog['name']} {genders[dog['gender']]}   {dog['age']}살   {dog['weight']}kg")
            st.write(dog["note"])
        with cols[2]:
            # 편집 중이지 않을 때만 '수정' 버튼 노출
            if st.session_state.edit_idx is None:
                if st.button("수정", key=f"edit_{idx}"):
                    st.session_state.edit_idx = idx
                    st.rerun()

        # 만약 이 카드가 편집 대상이라면 form 열기
        if st.session_state.edit_idx == idx:
            with st.form(key=f"form_{idx}"):
                name    = st.text_input("이름", value=dog["name"])
                breed   = st.text_input("견종", value=dog["breed"])
                gender  = st.selectbox("성별", ["수컷","암컷"], index=0 if dog["gender"]=="수컷" else 1)
                age     = st.number_input("나이(살)", min_value=0, value=dog["age"], step=1)
                weight  = st.number_input("무게(kg)", min_value=0.0, value=dog["weight"], step=0.1, format="%.1f")
                note    = st.text_area("특이사항", value=dog["note"])
                submitted = st.form_submit_button("저장")
                canceled  = st.form_submit_button("취소")

                if submitted:
                    # 세션 스테이트에 반영
                    st.session_state.dogs[idx] = {
                        "name": name,
                        "breed": breed,
                        "gender": gender,
                        "age": age,
                        "weight": round(weight, 1),
                        "note": note,
                        "img": dog["img"]
                    }
                    st.success("저장되었습니다.")
                    st.session_state.edit_idx = None
                    st.rerun()

                if canceled:
                    st.info("수정이 취소되었습니다.")
                    st.session_state.edit_idx = None
                    st.rerun()

        st.markdown("---")

    # + 버튼 (새 강아지 등록)
    c1, c2, c3 = st.columns([3,1,3])
    with c2:
        if st.button("➕"):
            st.info("새 강아지 등록 폼 열기")