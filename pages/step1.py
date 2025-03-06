"""Main chat interface for the EU-AI Act Analysis Tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from llmling_agent import ChatMessage
import streamlit as st

from components.chat_view import render_tool_call
from components.sidebar import render_agent_sidebar
from components.state import state


if TYPE_CHECKING:
    from llmling_agent.tools.tool_call_info import ToolCallInfo


async def main_async() -> None:
    """Async main function for the chat interface."""
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ticket erstellen", use_container_width=True):
            st.switch_page("pages/step2.py")

    with col2:
        if st.button("Neue Unterhaltung", use_container_width=True):
            # Clear chat history for now (NOOP otherwise)
            state.clear_agent_messages(state.chat_agent.name)
            st.rerun()  # Refresh the page to show empty chat

    await state.initialize()
    st.title("🤖 EU-AI Act Analyse Tool - Chat")

    # Configure the chat agent
    chat_agent = state.chat_agent
    render_agent_sidebar(chat_agent)

    # Display chat history
    for message in state.chat_messages:
        with st.chat_message(message.role):
            st.markdown(message.content)
            for tool_call in message.tool_calls:
                render_tool_call(st, tool_call)

    # Chat input
    if prompt := st.chat_input("Ihre Frage..."):
        # Add user message to chat history
        chat_message = ChatMessage(content=prompt, role="user")
        state.chat_messages.append(chat_message)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                # Stream the response
                with st.spinner("Denke nach..."):

                    def render(call: ToolCallInfo):
                        render_tool_call(st, call)

                    chat_agent.tool_used.connect(render)
                    full_response = await chat_agent.run(prompt)
                    st.markdown(full_response.content)
                    chat_agent.tool_used.disconnect(render)
                state.chat_messages.append(full_response)

        except Exception as e:  # noqa: BLE001
            error_msg = f"Ein Fehler ist aufgetreten: {e!s}"
            st.error(error_msg)


def main() -> None:
    """Main entry point for the chat interface."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
