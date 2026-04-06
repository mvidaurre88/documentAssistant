import streamlit as st

def go_to(screen_name):
    st.session_state.current_screen = screen_name
    st.rerun()