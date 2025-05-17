# ui
import streamlit as st
from services.calendar_api import calendar_api

def calendar_page():
    calendar_api()