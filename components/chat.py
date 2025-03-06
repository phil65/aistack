"""Chat UI component for streamlit applications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmling_agent.messaging.messages import ChatMessage
import streamlit as st

from components.state import state


if TYPE_CHECKING:
    from llmling_agent import Agent
    from streamlit.delta_generator import DeltaGenerator


async def stream_response(
    agent: Agent[None],
    prompt: str,
    placeholder: DeltaGenerator,
) -> None:
    """Stream response and collect messages directly to state."""

    # Function to collect messages directly to state
    async def collect_message(msg: ChatMessage) -> None:
        messages = state.messages[agent.name]
        if msg not in messages:
            messages.append(msg)

    # Connect to agent events
    agent.message_sent.connect(collect_message)
    agent.message_received.connect(collect_message)

    try:
        async with agent.run_stream(prompt) as stream:
            async for chunk in stream.stream():
                placeholder.markdown(chunk)
    finally:
        agent.message_sent.disconnect(collect_message)
        agent.message_received.disconnect(collect_message)


async def return_response(
    agent: Agent[None],
    prompt: str,
) -> None:
    """Get response with messages collected directly to state."""

    # Function to collect messages directly to state
    async def collect_message(msg: ChatMessage) -> None:
        messages = state.messages[agent.name]
        if msg not in messages:
            messages.append(msg)

    # Connect to agent events
    agent.message_sent.connect(collect_message)
    agent.message_received.connect(collect_message)

    try:
        await agent.run(prompt)  # We collect messages via events
    finally:
        agent.message_sent.disconnect(collect_message)
        agent.message_received.disconnect(collect_message)


def clear_chat_history(agent: Agent[None]) -> None:
    """Clear the chat history for a specific agent."""
    state.messages[agent.name] = []


async def create_chat_ui(
    agent: Agent[None],
    *,
    placeholder_text: str = "Ihre Frage...",
    thinking_text: str = "Denke nach...",
) -> None:
    """Create a chat UI that integrates with page's session state."""
    # Get messages for this specific agent
    messages = state.messages[agent.name]

    # Display chat history
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # Chat input
    if prompt := st.chat_input(placeholder_text):
        # Add and display user message
        user_msg = ChatMessage(content=prompt, role="user")
        messages.append(user_msg)

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Process message through agent
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                # Stream the response - messages are collected directly to state
                with st.spinner(thinking_text):
                    await stream_response(
                        agent=agent,
                        prompt=prompt,
                        placeholder=message_placeholder,
                    )

        except Exception as e:  # noqa: BLE001
            error_msg = f"Ein Fehler ist aufgetreten: {e!s}"
            st.error(error_msg)


if __name__ == "__main__":
    from llmling_agent import Agent

    from utils import run

    async def demo():
        await state.initialize()
        agent = Agent[None](model="gpt-4o-mini", name="test_agent")
        await agent.__aenter__()
        try:
            await create_chat_ui(agent)
        finally:
            await agent.__aexit__(None, None, None)

    run(demo())
