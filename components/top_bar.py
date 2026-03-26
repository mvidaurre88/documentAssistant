import streamlit as st
from navigation import go_to
from builder import render_stepper

def top_bar(title="", back_to=None, show_stepper=False, step=0):

    # contenedor real de Streamlit
    container = st.container()

    with container:
        col1, col2, col3 = st.columns([1, 8, 1])

        with col1:
            if back_to:
                if st.button("← Volver", use_container_width=True):
                    go_to(back_to)

        with col2:
            if show_stepper:
                render_stepper(st, step)

        if(title is not ""):
            st.markdown(
                f"<h3 style='text-align:center; margin-bottom: 30px;'>{title}</h3>",
                unsafe_allow_html=True
            )