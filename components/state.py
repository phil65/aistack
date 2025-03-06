"""State management for the Streamlit application."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from llmling_agent import Agent, AnyAgent, ChatMessage, StructuredAgent
import streamlit as st

from config import FormData


CHAT_AGENT_SYS_PROMPT = """\
Du bist Uschi. Dein Umgangston ist sehr ruppig. Du bist dafür verantwortlich, möglichst unfreundlich
dem User beim Bewältigen seiner Aufgaben zu helfen.
"""

TICKET_CREATOR_SYS_PROMPT = """\
Du bist verantwortllich, Tickets im Jira-TicketSystem zu erstellen.
Extrahiere Informationen aus dem dir gegebenen Chatverlauf.
"""

MODEL_NAME = "openrouter:openai/gpt-4o-mini"
CHAT_AGENT_NAME = "Dieter"
FORM_AGENT_NAME = "Uschi"


class State:
    """Session state management."""

    async def initialize(self) -> None:
        """Initialize all agents."""
        if "agents" not in st.session_state:
            # Initialize form agent
            form_agent: StructuredAgent[None, FormData] = Agent(
                name=FORM_AGENT_NAME,
                model=MODEL_NAME,
                system_prompt=CHAT_AGENT_SYS_PROMPT,
                session=False,
            ).to_structured(FormData)
            await form_agent.__aenter__()

            # Initialize chat agent
            chat_agent = Agent[None](
                name=CHAT_AGENT_NAME,
                model=MODEL_NAME,
                system_prompt=TICKET_CREATOR_SYS_PROMPT,
                session=False,
            )
            await chat_agent.__aenter__()

            st.session_state.agents = {
                form_agent.name: form_agent,
                chat_agent.name: chat_agent,
            }

        if "form_data" not in st.session_state:
            st.session_state.form_data = {field: "" for field in FormData.model_fields}

        if "messages" not in st.session_state:
            st.session_state.messages = defaultdict(list)
        if "agent_tools" not in st.session_state:
            st.session_state.agent_tools = defaultdict(list)

    @property
    def messages(self) -> defaultdict[str, list[ChatMessage[Any]]]:
        """Get all agent messages, indexed by agent name."""
        return st.session_state.messages

    @property
    def agent_tools(self):
        return st.session_state.agent_tools

    def clear_agent_messages(self, agent_name: str) -> None:
        """Clear messages for a specific agent."""
        self.messages[agent_name] = []

    @property
    def agents(self) -> dict[str, AnyAgent[Any, Any]]:
        """Get the agents dictionary, keyed by agent name."""
        return st.session_state.agents

    @property
    def form_agent(self) -> StructuredAgent[None, FormData]:
        """Get the session's form processing agent."""
        return st.session_state.agents[FORM_AGENT_NAME]

    @property
    def chat_agent(self) -> Agent[None]:
        """Get the session's chat agent."""
        return st.session_state.agents[CHAT_AGENT_NAME]

    @property
    def form_data(self) -> dict[str, str]:
        """Get the current form data."""
        return st.session_state.form_data

    @form_data.setter
    def form_data(self, value: dict[str, str]) -> None:
        """Set the current form data."""
        st.session_state.form_data = value

    @property
    def chat_messages(self) -> list[ChatMessage[Any]]:
        """Get the chat message history for the default chat agent."""
        return self.messages[CHAT_AGENT_NAME]

    @property
    def completed_form(self) -> FormData:
        """Get the completed form data."""
        return st.session_state.completed_form


state = State()
