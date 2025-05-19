import streamlit as st

# 강아지 성별 아이콘
genders = {"수컷":"♂️", "암컷":"♀️"}
# 강아지 견종 이미지
dog_imgs = {
    "포메라니안": "https://www.dailysecu.com/news/photo/202104/123449_145665_1147.png",
    "웰시코기":    "https://images.mypetlife.co.kr/content/uploads/2021/10/19151330/corgi-g1a1774f95_1280-1024x682.jpg"
}

# — 초기화 —
if "dogs" not in st.session_state:
    st.session_state.dogs = []            # 신규 이용자는 빈 리스트
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "adding" not in st.session_state:
    st.session_state.adding = False
if "add_errors" not in st.session_state:
    st.session_state.add_errors = {}      # 필드별 오류 플래그를 담는 dict

def dog_info():
    # 1) 등록된 강아지 없을 때 안내
    if not st.session_state.dogs:
        st.info("등록된 강아지가 없습니다. ➕ 버튼을 눌러 새 강아지를 등록해 보세요.")
    
    # 2) 기존 카드 & 수정 폼
    for idx, dog in enumerate(st.session_state.dogs):
        cols = st.columns([1,5,1])
        img = dog_imgs.get(dog["breed"],
               "https://cdn-icons-png.flaticon.com/512/608/608502.png")
        with cols[0]:
            st.image(img, width=200)
        with cols[1]:
            st.markdown(
                f"### {dog['name']} {genders[dog['gender']]}   "
                f"{dog['age']}살   {dog['weight']:.1f}kg"
            )
            st.write(dog["note"])
        with cols[2]:
            if st.session_state.edit_idx is None:
                if st.button("수정", key=f"edit_{idx}"):
                    st.session_state.edit_idx = idx
                    st.rerun()
        
        # 편집 대상 카드라면 폼 표시
        if st.session_state.edit_idx == idx:
            with st.form(key=f"form_{idx}"):
                name   = st.text_input("이름",    value=dog["name"])
                breed  = st.text_input("견종",    value=dog["breed"])
                gender = st.selectbox(
                    "성별", ["수컷","암컷"],
                    index=0 if dog["gender"]=="수컷" else 1
                )
                age    = st.number_input("나이(살)", min_value=1,
                                         value=dog["age"], step=1)
                weight = st.number_input("무게(kg)", min_value=0.1,
                                         value=dog["weight"], step=0.1,
                                         format="%.1f")
                note   = st.text_area("특이사항", value=dog["note"])
                
                submitted = st.form_submit_button("저장")
                canceled  = st.form_submit_button("취소")
                
                if submitted:
                    # 수정할 필드만 update
                    updated = {
                        "name":   name.strip(),
                        "breed":  breed.strip(),
                        "gender": gender,
                        "age":    age,
                        "weight": round(weight,1),
                        "note":   note
                    }
                    st.session_state.dogs[idx].update(updated)
                    st.session_state.edit_idx = None
                    st.rerun()
                
                if canceled:
                    st.session_state.edit_idx = None
                    st.rerun()
        
        st.markdown("---")
    
    # 3) ➕ 버튼: 등록 모드 진입
    if st.session_state.edit_idx is None and not st.session_state.adding:
        c1, c2, c3 = st.columns([3,1,3])
        with c2:
            if st.button("➕"):
                st.session_state.adding = True
                st.session_state.add_errors = {}
    
    # 4) 신규 등록 폼
    if st.session_state.adding:
        container = (
            st.modal("🐶 새 강아지 등록", key="add_modal")
            if hasattr(st, "modal")
            else st.expander("🐶 새 강아지 등록", expanded=True)
        )
        with container:
            with st.form("add_dog_form"):
                name   = st.text_input("이름", key="new_name")
                if st.session_state.add_errors.get("name"):
                    st.markdown(
                        '<span style="color:red">이 항목은 필수로 입력해주세요.</span>',
                        unsafe_allow_html=True
                    )
                
                breed  = st.text_input("견종", key="new_breed")
                if st.session_state.add_errors.get("breed"):
                    st.markdown(
                        '<span style="color:red">이 항목은 필수로 입력해주세요.</span>',
                        unsafe_allow_html=True
                    )
                
                gender = st.selectbox("성별", ["","수컷","암컷"], key="new_gender")
                if st.session_state.add_errors.get("gender"):
                    st.markdown(
                        '<span style="color:red">이 항목은 필수로 선택해주세요.</span>',
                        unsafe_allow_html=True
                    )
                
                age    = st.number_input("나이(살)", min_value=0, step=1,
                                         key="new_age")
                if st.session_state.add_errors.get("age"):
                    st.markdown(
                        '<span style="color:red">0 이상이어야 합니다.</span>',
                        unsafe_allow_html=True
                    )
                
                weight = st.number_input("무게(kg)", min_value=0.0, step=0.1,
                                         format="%.1f", key="new_weight")
                if st.session_state.add_errors.get("weight"):
                    st.markdown(
                        '<span style="color:red">0보다 커야 합니다.</span>',
                        unsafe_allow_html=True
                    )
                # 에러 메세지 출력
                # st.rerun()

                note   = st.text_area("특이사항", key="new_note")
                
                ok     = st.form_submit_button("확인")
                cancel = st.form_submit_button("취소")
                
                if ok:
                    # 필수 항목 검증
                    errs = {}
                    if not st.session_state.new_name.strip():   errs["name"]   = True
                    if not st.session_state.new_breed.strip():  errs["breed"]  = True
                    if not st.session_state.new_gender:         errs["gender"] = True
                    if st.session_state.new_age <= 0:           errs["age"]    = True
                    if st.session_state.new_weight <= 0:        errs["weight"] = True
                    
                    if errs:
                        st.session_state.add_errors = errs
                    else:
                        st.session_state.dogs.append({
                            "name":   st.session_state.new_name.strip(),
                            "breed":  st.session_state.new_breed.strip(),
                            "gender": st.session_state.new_gender,
                            "age":    st.session_state.new_age,
                            "weight": round(st.session_state.new_weight,1),
                            "note":   st.session_state.new_note,
                            # 여기에 나머지 키들 기본값 설정
                            "feed_period": "", "feed_time": "",
                            "walk_period": "", "walk_time": "",
                            "vaccination_period": "", "vaccination_time": "",
                            "bath_period": "", "bath_time": "",
                            "anthelmintic_period": "", "anthelmintic_time": "",
                        })
                        # 초기화 & 닫기
                        st.session_state.adding = False
                        for k in [
                            "add_errors","new_name","new_breed",
                            "new_gender","new_age","new_weight","new_note"
                        ]:
                            st.session_state.pop(k, None)
                    st.rerun()
                
                if cancel:
                    st.session_state.adding = False
                    for k in [
                        "add_errors","new_name","new_breed",
                        "new_gender","new_age","new_weight","new_note"
                    ]:
                        st.session_state.pop(k, None)
                    st.rerun()
