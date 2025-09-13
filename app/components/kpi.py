from __future__ import annotations

import streamlit as st


def kpi_card(label: str, value: str, delta: str | None = None, help_text: str | None = None, key: str | None = None):
    c = st.container()
    with c:
        col1, col2 = st.columns([2, 1], vertical_alignment="center")
        with col1:
            st.metric(label=label, value=value, delta=delta, help=help_text)
        with col2:
            st.write("")
    st.divider()

