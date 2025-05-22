import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import get_calendar_events, session_set_calendar_list, del_calendar_events, update_calendar_events
from services.tasks_api import tasks_api
# 날짜 입력용
from datetime import datetime, time, timedelta
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
###
        
###            
            # 구글 테스크 정보 추가
            checked=st.checkbox("구글 Tasks", value=True)
            if checked:
                calendar_events.extend(tasks_api())
            
            session.calendar_events=calendar_events
        #테스트 올 딜리트
        if st.button("🗑️ 올 딜리트"):
            st.info(calendar_events)
            for calendar_event in calendar_events:
                if "event_id" in calendar_event:
                    try:
                        del_calendar_events(calendar_event.get("event_id"))
                    except:
                        pass
            pass
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
            event.get("extendedProps", {}).get("calendar_summary", "구글 Tasks(수정불가)")
        )
        calendar_event_id=(
            event.get("extendedProps", {}).get("event_id", "이벤트 아이디 오류")
        )

        if all_day and "end" in event: #구글 캘린더와 st캘린더의 출력방식 맞추기(테스크는 end가 없어서 제외)
            end_date = datetime.strptime(end, "%Y-%m-%d")  # 문자열 → datetime
            end_plus_one = end_date + timedelta(days=-1)        # -1 더하기
            end=end_plus_one.strftime("%Y-%m-%d")  # 다시 문자열로 저장
        
        with st.expander(f"📌 선택한 이벤트 :  {title}"):
            if "box" in st.session_state:
                st.write(st.session_state.box)
            with st.container(border=True):
                #st.markdown(f"**제목:** {title}")
                st.markdown(f"**시작일:** {start}")
                if end:
                    st.markdown(f"**종료일:**  {end}")
                st.markdown(f"**종일 여부:**  {'예' if all_day else '아니오'}")
                st.markdown(f"**설명:**  {description}")
                #st.markdown(f"**캘린더 아이디:** `{calendar_id_print}`")
                st.markdown(f"**캘린더 위치:**  {calendar_summary}")
                #st.markdown(f"**이벤트 아이디:** `{calendar_event_id}`")
        ###

            
            
            
            '''
            , {'title': '새해첫날', 'start': '2020-01-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200101_bpdhmhbv4qqsbcul6gbt85mc28', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-01-02', 'allDay': True}, {'title': '설날', 'start': '2020-01-25', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200125_4hcn5s0k8c69lfufg2ajhmsg4c', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-01-26', 'allDay': True}, {'title': '설날 연휴', 'start': '2020-01-25', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200125_7esp9negdlb0g5sakv0knd5cug', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-01-26', 'allDay': True}, {'title': '설날 연휴', 'start': '2020-01-27', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200127_28ugqdtt1rog6cje277r31cr28', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-01-28', 'allDay': True}, {'title': '삼일절', 'start': '2020-03-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200301_3jm1p6d2gtd6sr8c4h7e8kkp1c', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-03-02', 'allDay': True}, {'title': '식목일', 'start': '2020-04-05', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200405_pdt7o43j04h9g1p2tef21ti348', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-04-06', 'allDay': True}, {'title': '국회의원선거일', 'start': '2020-04-15', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200415_2lime5jd535trrqh392sn3kodg', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-04-16', 'allDay': True}, {'title': '부처님오신날', 'start': '2020-04-30', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200430_hmj3dj5o24ujihnbgnjgm78hqk', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-05-01', 'allDay': True}, {'title': '노동절', 'start': '2020-05-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200501_vog7hrigkj8s968u7j9vnahlck', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-05-02', 'allDay': True}, {'title': '어린이날', 'start': '2020-05-05', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200505_vu9flbb55adr7obktfhvo86i2g', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-05-06', 'allDay': True}, {'title': '어버이날', 'start': '2020-05-08', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200508_ob6l8dmka3gfbor40192206hbg', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-05-09', 'allDay': True}, {'title': '스승의날', 'start': '2020-05-15', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200515_m1tvi35c7f8hmcn70g7aqb6jsk', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-05-16', 'allDay': True}, {'title': '현충일', 'start': '2020-06-06', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200606_s1if1euluao662q7q99cv96gic', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-06-07', 'allDay': True}, {'title': '제헌절', 'start': '2020-07-17', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200717_f0dm3q7hcoo7olvpl1c7oltfkg', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-07-18', 'allDay': True}, {'title': '광복절', 'start': '2020-08-15', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200815_bk9it0ninf3pap9citjb3iieg8', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-08-16', 'allDay': True}, {'title': '임시 휴일', 'start': '2020-08-17', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200817_75kt9r8h12b4rr42o1qjvmnejo', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-08-18', 'allDay': True}, {'title': '추석 연휴', 'start': '2020-09-30', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20200930_bu2nnrq9p2600c93m3814mn33s', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-01', 'allDay': True}, {'title': '추석', 'start': '2020-10-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201001_0bfsktmp93o1ufckq68i5qrlks', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-02', 'allDay': True}, {'title': '국군의날', 'start': '2020-10-01', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201001_vsujlo8ubhskkdsb8v0eg1gbg0', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-02', 'allDay': True}, {'title': '추석 연휴', 'start': '2020-10-02', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201002_d4qmul3pbnsseupd0iulubu9pc', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-03', 'allDay': True}, {'title': '개천절', 'start': '2020-10-03', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201003_dtrl6a268etcghmn2h5iu1ghds', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-04', 'allDay': True}, {'title': '한글날', 'start': '2020-10-09', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201009_lseiibdmcqt381j0njifj3kvi0', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-10-10', 'allDay': True}, {'title': '크리스마스 이브', 'start': '2020-12-24', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201224_u866a1piicgedodpsc97uaa8fc', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-12-25', 'allDay': True}, {'title': '크리스마스', 'start': '2020-12-25', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201225_rjbpjplbt067238r9djfl1e064', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2020-12-26', 'allDay': True}, {'title': '섣달 그믐날', 'start': '2020-12-31', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20201231_2daktqrpsp257nbe52bjcav8mg', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-01-01', 'allDay': True}, {'title': '새해첫날', 'start': '2021-01-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210101_qskcm7cd5mtgrb19d18fe5qrp8', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-01-02', 'allDay': True}, {'title': '설날', 'start': '2021-02-12', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210212_jiib4ogj3lmnshllove8ft5suo', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-02-13', 'allDay': True}, {'title': '설날 연휴', 'start': '2021-02-12', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210212_llam28icmk8irbhv057rbtcors', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-02-13', 'allDay': True}, {'title': '설날 연휴', 'start': '2021-02-13', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210213_pnpg2v79so9t38mfpbifd0dplc', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-02-14', 'allDay': True}, {'title': '삼일절', 'start': '2021-03-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210301_o8rburnitvru9n62n4jivd2dho', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-03-02', 'allDay': True}, {'title': '식목일', 'start': '2021-04-05', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210405_3usgpo8b7f522goob19eb31qc4', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-04-06', 'allDay': True}, {'title': '노동절', 'start': '2021-05-01', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210501_aupt9u76cr154eoid5bs44auug', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-05-02', 'allDay': True}, {'title': '어린이날', 'start': '2021-05-05', 'resourceId': 'a', 'description': '공휴일', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'event_id': '20210505_pv1i96v2k99v2ohprf31m19330', 'calendar_summary': '대한민국의 휴일', 'all_day': True, 'end': '2021-05-06', 'allDay': True}, {'title': '어버이날', 'start': '2021-05-08', 'resourceId': 'a', 'description': '기념일\n기념일을 숨기려면 Google Calendar 설정 > 대한민국의 휴일 캘린더로 이동하세요.', 'calendar_id': 'ko.south_korea#holiday@group.v.calendar.google.com', 'eve
            '''
            
        # 수정 모드 토글
        with st.expander("✏️ 이벤트 수정/삭제"):
            new_title = st.text_input("제목", value=title)
            new_description = st.text_area("설명", value=description)
            tz = pytz.timezone("Asia/Seoul")

            new_all_day = st.checkbox("종일 여부", value=all_day)

            if new_all_day:
                new_start_date = st.date_input("📅 시작 날짜", value=start[:10])
                new_end_date = st.date_input("📅 종료 날짜", value=end[:10] if end else new_start_date)

                start_obj = {"date": str(new_start_date)}
                end_obj = {"date": str(new_end_date + timedelta(days=1))}

            else:
                def parse_dt(dt_str, default_dt):
                    try:
                        return datetime.fromisoformat(dt_str)
                    except:
                        return default_dt
            
                default_start_dt = parse_dt(start, datetime.now().replace(hour=9, minute=0))
                default_end_dt = parse_dt(end, datetime.now().replace(hour=10, minute=0))

                start_date = st.date_input("📅 시작 날짜", value=default_start_dt.date())
                end_date = st.date_input("📅 종료 날짜", value=default_end_dt.date())

                st.markdown("⏰ 시작 시간")
                col1, col2 = st.columns(2)
                with col1:
                    start_hour = st.selectbox("시", list(range(0, 24)), index=default_start_dt.hour)
                with col2:
                    start_minute = st.selectbox("분", list(range(0, 60)), index=default_start_dt.minute)

                st.markdown("⏰ 종료 시간")
                col3, col4 = st.columns(2)
                with col3:
                    end_hour = st.selectbox("시 ", list(range(0, 24)), index=default_end_dt.hour)
                with col4:
                    end_minute = st.selectbox("분 ", list(range(0, 60)), index=default_end_dt.minute)

                start_time_obj = time(start_hour, start_minute)
                end_time_obj = time(end_hour, end_minute)

                tz = pytz.timezone("Asia/Seoul")
                start_dt = tz.localize(datetime.combine(start_date, start_time_obj))
                end_dt = tz.localize(datetime.combine(end_date, end_time_obj))

                start_obj = {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "Asia/Seoul"
                }
                end_obj = {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "Asia/Seoul"
                }

            if st.button("✅ 수정 저장"):
                update_calendar_events(
                    event_id=calendar_event_id,
                    summary=new_title,
                    description=new_description,
                    start_time=start_obj,
                    end_time=end_obj,
                    allDay=new_all_day,
                    calendar_id=calendar_id_print
                )

            # 삭제 확인 후 실행
            if st.button("🗑️ 이 이벤트 삭제"):
                del_calendar_events(calendar_event_id, calendar_id_print)
                
            if st.button("화면 갱신"):
                st.rerun()




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