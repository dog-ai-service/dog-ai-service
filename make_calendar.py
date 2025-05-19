'''
    캘린더 만드는 함수 
        - get_today_events로 오늘 하루의 일정을 가져옴
'''

import streamlit as st
from streamlit_calendar import calendar
from datetime import date
from googlecalendar.get_today_events import get_today_events


# 오늘 날짜
today = date.today().isoformat()

# 캘린더 컴포넌트 렌더링 함수 -> 메인 페이지
def init_calendar():
    st.markdown("## 강아지를 위한 AI 캘린더 서비스 📆")
    st.markdown("강아지의 생일, 예방접종, 약속 등을 관리할 수 있는 캘린더 서비스입니다. \n"
                "AI가 강아지의 나이를 계산하고, 예방접종 일정을 알려줍니다.")
    
    # 오늘 일정 가져오기
    today_events = get_today_events()

    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "initialDate": today,
        "initialView": "dayGridDay",
    }

    state = calendar(
        events=today_events,
        options=calendar_options,
        custom_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
            font-size: 1.4rem;  /* 이벤트 시간 폰트 크기 증가 */
        }
        .fc-event-title {
            font-weight: 700;
            font-size: 1.4rem;  /* 이벤트 제목 폰트 크기 증가 */
        }
        .fc-toolbar-title {
            font-size: 2.5rem;  /* 툴바 제목 폰트 크기 기존 2rem에서 증가 */
        }
        .fc {
            font-size: 1.1rem;  /* 캘린더 전체 기본 폰트 크기 증가 */
        }
    """
    )

    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

init_calendar()