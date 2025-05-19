import streamlit as st
from streamlit_calendar import calendar as cld
from services.calendar_api import calendar_api

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
    calendar_events = calendar_api()
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

    calendar = cld(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
        key='calendar', # Assign a widget key to prevent state loss
        )

