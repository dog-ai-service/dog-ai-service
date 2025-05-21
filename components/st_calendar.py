import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import get_calendar_events, session_set_calendar_list, del_calendar_events, update_calendar_events
from services.tasks_api import tasks_api
# 날짜 입력용
from datetime import datetime, time
import pytz

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
###
            # 수정 모드 토글
            with st.expander("✏️ 이벤트 수정"):
                new_title = st.text_input("제목", value=title)
                new_description = st.text_area("설명", value=description)
                tz = pytz.timezone("Asia/Seoul")

                # 사용자 입력값 받기
                new_all_day = st.checkbox("종일 여부", value=all_day)
                new_start_date = st.date_input("📅 시작날짜", value=start[:10])
                new_end_date = st.date_input("📅 종료날짜", value=end[:10] if end else None)

                if new_all_day:
                    # 종일 이벤트일 경우: date만 사용
                    start_iso = datetime.strptime(str(new_start_date), "%Y-%m-%d").date().isoformat()
                    end_iso = datetime.strptime(str(new_end_date), "%Y-%m-%d").date().isoformat()
                    start = {"date": start_iso}
                    end = {"date": end_iso}
                else:
                    # 시간 정보도 있는 이벤트
                    original_start_dt = datetime.fromisoformat(start) if isinstance(start, str) and 'T' in start else None
                    original_end_dt = datetime.fromisoformat(end) if end and isinstance(end, str) and 'T' in end else None

                    start_hour = original_start_dt.hour if original_start_dt else 9
                    start_minute = original_start_dt.minute if original_start_dt else 0

                    end_hour = original_end_dt.hour if original_end_dt else 10
                    end_minute = original_end_dt.minute if original_end_dt else 0

                    # 시간 분 선택값 적용
                    start_hour = st.selectbox("시작 시간 (시)", list(range(0, 24)), index=start_hour)
                    start_minute = st.selectbox("시작 시간 (분)", list(range(0, 60)), index=start_minute)

                    end_hour = st.selectbox("종료 시간 (시)", list(range(0, 24)), index=end_hour)
                    end_minute = st.selectbox("종료 시간 (분)", list(range(0, 60)), index=end_minute)
                    
                    new_start_time = time(hour=start_hour, minute=start_minute)
                    new_end_time = time(hour=end_hour, minute=end_minute)

                    start_dt = tz.localize(datetime.combine(new_start_date, new_start_time))
                    end_dt = tz.localize(datetime.combine(new_end_date, new_end_time))

                    start = {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Seoul"}
                    end = {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Seoul"}

                if st.button("✅ 수정 저장"):
                    update_calendar_events(
                        event_id=calendar_event_id,
                        summary=new_title,
                        description=new_description,
                        start_time=start,
                        end_time=end,
                        allDay=new_all_day,
                        calendar_id=calendar_id
                    )
##
            # 삭제 버튼
            if st.button("🗑️ 이 이벤트 삭제"):
                del_calendar_events(calendar_event_id, calendar_id_print)
                st.rerun()
                st.success("✅ 이벤트를 성공적으로 삭제했습니다.")




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