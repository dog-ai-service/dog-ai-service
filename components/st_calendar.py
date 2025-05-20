import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import calendar_api, get_calendar_id
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
    prev_calendar=None if "selected_calendar" not in st.session_state else st.session_state.selected_calendar
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
    get_calendar_id()
    
    if "selected_calendar" in st.session_state:
        if prev_calendar is not st.session_state.selected_calendar:
            st.info(st.session_state.selected_calendar)
            
            tasks_api_data=tasks_api()
            calendar_api_data=calendar_api()
            if tasks_api_data is not None:
                calendar_events.extend(tasks_api_data)
            if calendar_api_data is not None:
                calendar_events.extend(calendar_api_data)
        cld(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key=f'calendar_{st.session_state.selected_calendar}', # Assign a widget key to prevent state loss
        )
