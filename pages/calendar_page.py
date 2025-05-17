# ui
import streamlit as st
from services.calendar_api import calendar_api
from components.st_calendar import st_calendar

def calendar_page():
    st_calendar()
    calendar_api()