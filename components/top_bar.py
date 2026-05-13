import streamlit as st
from utils.navigation import go_to
from components.stepper import render_stepper

def top_bar(title="", back_to=None, show_stepper=False, step=0, key=""):

    container = st.container()
    with container:
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 8, 3])

        with col1:
            if st.button("Inicio", use_container_width=True, type="secondary", key=f"btn_inicio_{key}"):
                go_to("init")
    
        with col2:
            if back_to:
                if st.button("← Volver", use_container_width=True, type="secondary", key=f"btn_volver_{key}"):
                    go_to(back_to)
    
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([1, 11, 1])
        with col2:
            if show_stepper:
                render_stepper(step)

        if title != "":
            st.markdown(f"<h4 style='text-align:center;'>{title}</h4>", unsafe_allow_html=True)