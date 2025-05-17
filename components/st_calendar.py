import streamlit as st
from streamlit_calendar import calendar as cld

def st_calendar():
    calendar_options = {
        "editable": True,
        "selectable": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "initialView": "dayGridMonth",
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
    }
    calendar_events = [
        {
            "title": "Event 1",
            "start": "2023-07-31T08:30:00",
            "end": "2023-07-31T10:30:00",
            "resourceId": "a",
        },
        {
            "title": "Event 2",
            "start": "2023-07-31T07:30:00",
            "end": "2023-07-31T10:30:00",
            "resourceId": "b",
        },
        {
            "title": "Event 3",
            "start": "2023-07-31T10:40:00",
            "end": "2023-07-31T12:30:00",
            "resourceId": "a",
        }
    ]
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

