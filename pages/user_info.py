'''
    사용자 정보 페이지
'''


from sidebar import sidebar
import streamlit as st


def user_info():
    st.title("🐶 반려견 정보")
    st.markdown("반려견의 프로필과 건강 정보를 한눈에 확인하세요!")
    st.image("pages/pudding1.jpg", width=300)
    left, right = st.columns([1, 2])

    # 예시 데이터 
    dog_profile = {
        "이름": "푸딩이",
        "견종": "말티푸",
        "성별": "남아",
        "나이": "6살",
        "몸무게": "4kg",
        "중성화 여부": "완료",
        "알레르기": "없음",
        "건강 메모": "건강"
    }
    
    with st.container():
        with left:
            st.subheader("📌 기본 정보")
            st.write(f"**이름:** {dog_profile['이름']}")
            st.write(f"**견종:** {dog_profile['견종']}")
            st.write(f"**성별:** {dog_profile['성별']}")
            st.write(f"**나이:** {dog_profile['나이']}")
            st.write(f"**몸무게:** {dog_profile['몸무게']}")
            st.write(f"**중성화 여부:** {dog_profile['중성화 여부']}")
        with right:
            st.subheader("📋 특이 사항")
            st.write(f"**알레르기:** {dog_profile['알레르기']}")
            st.write(f"**건강 메모:** {dog_profile['건강 메모']}")

        if st.button("✏️ 정보 수정하기"):
            st.info("추후 업데이트 예정 기능입니다. 😉")


sidebar()
user_info()
