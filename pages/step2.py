"""Ticket creation interface for the EU-AI Act Analysis Tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import streamlit as st

from components.primitives import render_model_form
from components.sidebar import render_agent_sidebar
from components.state import state


if TYPE_CHECKING:
    from llmling_agent import ChatMessage, StructuredAgent

    from config import FormData


async def process_chat_history(
    agent: StructuredAgent[None, FormData],
    chat_messages: list[ChatMessage],
) -> FormData:
    """Process the chat history and create a ticket summary."""
    # Format chat history into a single text
    chat_text = "\n\n".join(f"{msg.role.upper()}: {msg.content}" for msg in chat_messages)

    # Add instructions for ticket creation
    prompt = (
        "Based on the following chat conversation, create a ticket for our ticket system. "
        "Extract relevant information like the issue, priority, and any important details. "
        f"\n\nCHAT HISTORY:\n{chat_text}\n\n"
        "Please create a structured ticket with appropriate fields."
    )

    # Process with the agent
    result = await agent.run(prompt)
    return result.content  # This is a FormData instance


async def main_async() -> None:
    """Async main function for the ticket creation interface."""
    await state.initialize()
    st.title("🎫 EU-AI Act Analyse Tool - Ticket erstellen")

    # Configure the agent
    ticket_creator = state.form_agent
    render_agent_sidebar(ticket_creator)

    # Get chat history from the chat agent
    chat_messages = state.chat_messages

    if not chat_messages:
        st.warning(
            "Keine Chat-Nachrichten gefunden. Bitte führen Sie zuerst eine Unterhaltung."
        )
        if st.button("Zurück zum Chat", use_container_width=True):
            st.switch_page("pages/step1.py")
        return

    # Create ticket based on chat history
    with st.spinner("Ticket wird erstellt..."):
        ticket_data = await process_chat_history(ticket_creator, chat_messages)

    # Display and edit the form
    st.subheader("Generiertes Ticket")
    updated_ticket = render_model_form(ticket_data)

    # Download option (convert to text for download)
    ticket_text = (
        f"Title: {updated_ticket.title}\n\n"
        f"Description: {updated_ticket.description}\n\n"
        f"Requirements: {updated_ticket.requirements}\n\n"
        f"Constraints: {updated_ticket.constraints}\n\n"
        f"Additional Info: {updated_ticket.additional_info}"
    )

    st.download_button(
        label="Ticket als Text herunterladen",
        data=ticket_text,
        file_name="ticket.txt",
        mime="text/plain",
    )

    # Back button
    if st.button("Zurück zum Chat", use_container_width=True):
        st.switch_page("pages/step1.py")


def main() -> None:
    """Main entry point for the ticket creation interface."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
