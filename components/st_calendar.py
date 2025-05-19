import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import calendar_api
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
    calendar_events = [
        {
        "title":"더미",
        "start":"2020-01-01",
        "resourceId":"a",
        "allDay": True,
        }]
    tasks_api_data=tasks_api()
    calendar_api_data=calendar_api()
    if tasks_api_data is not None:
        calendar_events.extend(tasks_api_data)
    if calendar_api_data is not None:
        calendar_events.extend(calendar_api_data)

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
    #테스트 출력
    #st.write(calendar_events)

    calendar = cld(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
        key='calendar', # Assign a widget key to prevent state loss
        )

