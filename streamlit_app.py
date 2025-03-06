"""Welcome page for the EU-AI Act Analysis Tool."""

from __future__ import annotations

import sys

import streamlit as st


if sys.platform == "win32":
    import asyncio
    from asyncio import WindowsSelectorEventLoopPolicy

    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def main() -> None:
    """Render the welcome page."""
    st.title("🤖 EU-AI Act Analyse Tool")

    st.markdown("""
    ## Willkommen!

    Dieses Tool hilft Ihnen dabei, Informationen im Kontext des EU-AI Acts zu
    analysieren und zu strukturieren.

    ### Workflow:
    1. **Schritt 1**: Erfassen Sie die relevanten Informationen in einem
       strukturierten Format
    2. **Schritt 2**: Erhalten Sie eine detaillierte Analyse und können im Dialog
       weitere Fragen klären

    Klicken Sie auf 'Start', um zu beginnen.
    """)

    if st.button("Start", use_container_width=True):
        st.switch_page("pages/step1.py")


if __name__ == "__main__":
    main()
