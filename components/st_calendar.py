import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import get_calendar_events, session_set_calendar_list
from services.tasks_api import tasks_api

def st_calendar():
    calendar_options = {
        "editable": True,
        "selectable": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth,dayGridYear",
        },
        "initialView": "dayGridMonth",
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
    }

    custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """
    
    # 캘린더에 들어갈 이벤트 값
    calendar_events = [
        {
        "title":"더미",
        "start":"2020-01-01",
        "resourceId":"a",
        "allDay": True,
        }]
    
    # 세션
    session=st.session_state

    # 로그인 시 캘린더 목록이 없다면 캘린더 목록을 세션에 저장
    if "token" in session and "calendar_list" not in session:  
        session_set_calendar_list()

    if "calendar_list" in session and "token" in session:  # 세션에 캘린더 목록이 있다면
        calendar_list=session.calendar_list #세션의 캘린더 목록
        # 갱신을 위해 다시 생성
        # 캘린더에 들어갈 이벤트 값
        calendar_events = [
            {
            "title":"더미",
            "start":"2020-01-01",
            "resourceId":"a",
            "allDay": True,
            }
        ]
        calendar_data=None
        with st.expander("🗂️ 캘린더 선택"):
            # 캘린더마다 체크박스를 이용하여 추가
            for calendar_id in session.calendar_list.keys():
                checked=st.checkbox(calendar_list[calendar_id], value=True)
                if checked:
                    calendar_events.extend(get_calendar_events(calendar_id))
            
            # 구글 테스크 정보 추가
            checked=st.checkbox("구글 Tasks", value=True)
            if checked:
                calendar_events.extend(tasks_api())
            
            session.calendar_events=calendar_events

        calendar_data=cld(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key=f'calendar_{session.calendar_events}', #갱신용으로 calendar_events를 쓰면 비효율적이지만 현재로선 최선
        )
    else :
        calendar_data=cld(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key=f'calendar', # Assign a widget key to prevent state loss
        )

    # 이벤트 클릭 시 설명 박스 표시
    if calendar_data and calendar_data.get("callback") == "eventClick":
        #테스트
        st.info(f"이벤트 : {calendar_data}")
        event = calendar_data["eventClick"]["event"]
        title = event.get("title", "제목 없음")
        start = event.get("start", "시작일 없음")
        end = event.get("end", "")
        all_day = event.get("allDay", False)
        description = (
            event.get("extendedProps", {}).get("description", "설명 없음")
        )
        calendar_id_print=(
            event.get("extendedProps", {}).get("calendar_id", "아이디 없음")
        )
        calendar_summary=(
            event.get("extendedProps", {}).get("calendar_summary", "캘린더 아이디 오류")
        )
        calendar_event_id=(
            event.get("extendedProps", {}).get("event_id", "이벤트 아이디 오류")
        )

        st.markdown("### 📌 선택한 이벤트")
        with st.container(border=True):
            st.markdown(f"**제목:** `{title}`")
            st.markdown(f"**시작일:** `{start}`")
            if end:
                st.markdown(f"**종료일:** `{end}`")
            st.markdown(f"**종일 여부:** `{'예' if all_day else '아니오'}`")
            st.markdown(f"**설명:** `{description}`")
            st.markdown(f"**캘린더 아이디:** `{calendar_id_print}`")
            st.markdown(f"**캘린더 제목:** `{calendar_summary}`")
            st.markdown(f"**이벤트 아이디:** `{calendar_event_id}`")

            st.divider()

            # 수정 모드 토글
            with st.expander("✏️ 이벤트 수정"):
                new_title = st.text_input("제목", value=title)
                new_description = st.text_area("설명", value=description)
                new_start = st.text_input("시작일", value=start)
                new_end = st.text_input("종료일", value=end or "")
                new_all_day = st.checkbox("종일 이벤트", value=all_day)

                if st.button("✅ 수정 저장"):
                    # 여기서 수정 요청 처리 함수 호출 필요 (예: update_calendar_event)
                    st.success("수정된 이벤트 정보 저장 요청 완료 (예시)")
                    # 실제 적용은 API 연동 함수로!

            # 삭제 버튼
            if st.button("🗑️ 이 이벤트 삭제"):
                # 여기서 삭제 요청 처리 함수 호출 필요 (예: delete_calendar_event)
                st.warning("이벤트 삭제 요청 완료 (예시)")
                # 실제 삭제도 마찬가지로 API 연동 필요



'''
이벤트 예시
{
    "callback": "eventClick",
    "eventClick": {
        "event": {
            "allDay": False,
            "title": "이벤트 테스트1",
            "start": "2025-05-21T18: 30: 00+09: 00",
            "end": "2025-05-21T19: 30: 00+09: 00",
            "extendedProps": {
                "description": "이벤트 테스트1의 설명",
                "calendar_id": 캘린더의 id,
                "calendar_summary" : 캘린더의 제목,
                "eventId" : 이벤트의 아이디
            }
        },
        "view": {
            "type": "dayGridMonth",
            "title": "May 2025",
            "activeStart": "2025-04-26T15: 00: 00.000Z",
            "activeEnd": "2025-06-07T15: 00: 00.000Z",
            "currentStart": "2025-04-30T15: 00: 00.000Z",
            "currentEnd": "2025-05-31T15: 00: 00.000Z",
        }
    }
}
'''