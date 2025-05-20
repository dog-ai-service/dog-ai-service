'''
    - 강아지 데이터
        st.session_state.dogs = [
            {   
                # 입력받는 데이터 필드
                "name":   "이름",
                "breed":  "견종",
                "gender": "성별",
                "birth":  "생년월일",
                "weight": "무게",
                "note":   "특이사항",
                "de_sex": "중성화 여부", 
                # 계산되야 하는 데이터 필드
                "feed_period": "사료 주기", "feed_time": "사료 시각",
                "walk_period": "산책 주기", "walk_time": "산책 시각",
                "vaccination_period": "예방접종 주기", "vaccination_time": "예방접종 시각",
                "bath_period": "목욕 주기", "bath_time": "목욕 시각",
                "anthelmintic_period": "구충제 주기", "anthelmintic_time": "구충제 시각"
            }, 
            { ... }
        ]
'''
import streamlit as st
from components.dog_data import genders, dog_imgs, default_fields
from datetime import date

def init_state():
    if "dogs" not in st.session_state:
        st.session_state.dogs = []
    if "edit_idx" not in st.session_state:
        st.session_state.edit_idx = None
    if "adding" not in st.session_state:
        st.session_state.adding = False
    if "add_errors" not in st.session_state:
        st.session_state.add_errors = {}

def compute_age(birth: date) -> int:
    today = date.today()
    age = today.year - birth.year
    # 생일이 아직 안 지난 경우 -1
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age

def render_dog_card(dog, idx):
    cols = st.columns([1,5,1])
    img = dog_imgs.get(dog["breed"], default_fields["placeholder_img"])
    with cols[0]:
        st.image(img, width=200)
    with cols[1]:
        # compute_age() 로 나이 계산
        age = compute_age(dog["birth"])
        st.markdown(
                f"### {dog['name']} {genders[dog['gender']]}   "
                f"{age}살   {dog['weight']:.1f}kg"
            )
        st.write(dog["note"])
    with cols[2]:
        if st.session_state.edit_idx is None:
            if st.button("수정", key=f"edit_{idx}"):
                st.session_state.edit_idx = idx
                st.rerun()

def render_edit_form(idx, dog):
    # idx 번 강아지를 수정할 때만 호출
    with st.form(key=f"edit_form_{idx}"):
        name   = st.text_input("이름", value=dog["name"])
        breed  = st.text_input("견종", value=dog["breed"])
        gender = st.selectbox("성별", ["수컷","암컷"], index=0 if dog["gender"]=="수컷" else 1)
        birth  = st.date_input("생년월일", value=dog["birth"], min_value=date(2000,1,1), max_value=date.today())
        de_sex = st.selectbox("중성화", ["O","X"], index=0 if dog.get("de_sex","O")=="O" else 1)
        weight = st.number_input("무게(kg)", min_value=0.1, value=dog["weight"], step=0.1, format="%.1f")
        note   = st.text_area("특이사항", value=dog["note"])

        submitted = st.form_submit_button("저장")
        canceled  = st.form_submit_button("취소")

        if submitted:
            st.session_state.dogs[idx].update({
                "name":   name.strip(),
                "breed":  breed.strip(),
                "gender": gender,
                "birth":  birth,
                "de_sex": de_sex,
                "weight": round(weight,1),
                "note":   note
            })
            st.session_state.edit_idx = None
            st.rerun()

        if canceled:
            st.session_state.edit_idx = None
            st.rerun()

def render_add_button():
    # 수정 모드 아닐 때만 ➕ 노출
    if st.session_state.edit_idx is None and not st.session_state.adding:
        c1,c2,c3 = st.columns([3,1,3])
        with c2:
            if st.button("➕"):
                st.session_state.adding = True
                st.session_state.add_errors = {}

def render_add_form():
    # ➕ 호출
    if not st.session_state.adding:
        return

    # Modal 열기
    if hasattr(st, "modal"):
        container = st.modal("🐶 새 강아지 등록", key="add_modal")
    else:
        container = st.expander("🐶 새 강아지 등록", expanded=True)

    with container:
        with st.form("add_form"):
            # --- 입력 필드 ---
            name   = st.text_input("이름", key="new_name")
            if st.session_state.add_errors.get("name"):
                st.markdown('<span style="color:red">이 항목은 필수로 입력해주세요.</span>', unsafe_allow_html=True)

            breed  = st.text_input("견종", key="new_breed")
            if st.session_state.add_errors.get("breed"):
                st.markdown('<span style="color:red">이 항목은 필수로 입력해주세요.</span>', unsafe_allow_html=True)

            gender = st.selectbox("성별", ["수컷","암컷"], key="new_gender")
            if st.session_state.add_errors.get("gender"):
                st.markdown('<span style="color:red">이 항목은 필수로 선택해주세요.</span>', unsafe_allow_html=True)

            birth  = st.date_input("생년월일", value=date.today(), min_value=date(2000,1,1), max_value=date.today(), key="new_birth")
            if st.session_state.add_errors.get("birth"):
                st.markdown('<span style="color:red">필수 선택입니다.</span>', unsafe_allow_html=True)
            de_sex = st.selectbox("중성화 여부", ["O","X"], key="new_de_sex")

            weight = st.number_input("무게(kg)", min_value=0.0, step=0.1, format="%.1f", key="new_weight")
            if st.session_state.add_errors.get("weight"):
                st.markdown('<span style="color:red">0보다 커야 합니다.</span>', unsafe_allow_html=True)

            note   = st.text_area("특이사항", key="new_note")

            ok     = st.form_submit_button("확인")
            cancel = st.form_submit_button("취소")

            if ok:
                errs = {}
                if not st.session_state.new_name.strip():   errs["name"]   = True
                if not st.session_state.new_breed.strip():  errs["breed"]  = True
                if not st.session_state.new_gender:         errs["gender"] = True
                if not st.session_state.new_birth:          errs["birth"]  = True
                if st.session_state.new_weight < 0.1:       errs["weight"] = True

                if errs:
                    st.session_state.add_errors = errs
                else:
                    st.session_state.dogs.append({
                        "name":   st.session_state.new_name.strip(),
                        "breed":  st.session_state.new_breed.strip(),
                        "gender": st.session_state.new_gender,
                        "birth":  st.session_state.new_birth,
                        "de_sex": st.session_state.new_de_sex,
                        "weight": round(st.session_state.new_weight,1),
                        "note":   st.session_state.new_note,
                        "feed_period": "", "feed_time": "",
                        "walk_period": "", "walk_time": "",
                        "vaccination_period": "", "vaccination_time": "",
                        "bath_period": "", "bath_time": "",
                        "anthelmintic_period": "", "anthelmintic_time": "",
                    })
                    st.session_state.adding = False
                    # cleanup
                    for k in [
                        "add_errors","new_name","new_breed",
                        "new_gender","new_birth","new_weight","new_note"
                    ]:
                        st.session_state.pop(k, None)
                    st.rerun()

            if cancel:
                st.session_state.adding = False
                for k in [
                    "add_errors","new_name","new_breed",
                    "new_gender","new_birth","new_weight","new_note"
                ]:
                    st.session_state.pop(k, None)
                st.rerun()

def dog_info_page():
    init_state()
    if not st.session_state.dogs:
        st.info("등록된 강아지가 없습니다.")
    for idx, dog in enumerate(st.session_state.dogs):
        render_dog_card(dog, idx)
        if st.session_state.edit_idx == idx:
            render_edit_form(idx, dog)
        st.markdown("---")
    render_add_button()
    render_add_form()
    print(st.session_state.dogs)