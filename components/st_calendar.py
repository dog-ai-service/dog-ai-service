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
    
    st.write(f"📆 캘린더 정보 : {calendar_data}")

    # 이벤트 클릭 시 설명 박스 표시
    if calendar_data and calendar_data.get("callback") == "eventClick":
        event = calendar_data["eventClick"]["event"]
        title = event.get("title", "제목 없음")
        start = event.get("start", "시작일 없음")
        end = event.get("end", None)
        all_day = event.get("allDay", False)
        description=event.get("description", "설명없음")

        with st.container():
            st.markdown("### 📌 선택한 이벤트")
            st.info(f"**제목:** {title}")
            st.write(f"**시작일:** {start}")
            if end:
                st.write(f"**종료일:** {end}")
            st.write(f"**종일 여부:** {'✅ 예' if all_day else '❌ 아니오'}")
            st.info(f"**이벤트 설명:** {calendar_data.get("eventClick","이벤트클릭없음").get("event","이벤트없음").get("extendedProps","extendedProps없음").get("description","설명없음")}")

            # 필요한 경우 여기에 더 많은 필드 출력 가능
            # 예: event.get("description") 등
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
                "description": "이벤트 테스트1의 설명"
            }
        },
        "view": {
            "type": "dayGridMonth",
            "title": "May 2025",
            "activeStart": "2025-04-26T15: 00: 00.000Z",
            "activeEnd": "2025-06-07T15: 00: 00.000Z",
            "currentStart": "2025-04-30T15: 00: 00.000Z",
            "currentEnd": "2025-05-31T15: 00: 00.000Z"
        }
    }
}
'''