"""Chat message display component for streamlit."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from llmling_agent.messaging.messages import ChatMessage
import streamlit as st


if TYPE_CHECKING:
    import types

    from streamlit.delta_generator import DeltaGenerator


def render_tool_call(container: DeltaGenerator | types.ModuleType, tool_call):
    """Render a tool call in an expander."""
    with container.expander(f"🛠️ Tool: {tool_call.tool_name}", expanded=False):
        st.markdown("**Arguments:**")
        for name, value in tool_call.args.items():
            st.markdown(f"- `{name}`: {value}")
        if tool_call.result:
            st.markdown("**Result:**")
            st.markdown(f"\n{tool_call.result}\n")
        if tool_call.error:
            st.error(f"Error: {tool_call.error}")
        if tool_call.timing:
            st.markdown(f"*Execution time: {tool_call.timing:.2f}s*")


def render_message_content(msg: ChatMessage[Any], container: DeltaGenerator):
    """Render a message's content with optional metadata."""
    # Main content
    container.markdown(str(msg.content))

    # Show tool calls in expanders
    for tool_call in msg.tool_calls:
        render_tool_call(container, tool_call)

    # Optional metadata footer
    metadata = []
    if msg.model:
        metadata.append(f"Model: {msg.model}")
    if msg.cost_info:
        metadata.append(f"Cost: ${msg.cost_info.total_cost:.4f}")
        metadata.append(f"Tokens: {msg.cost_info.token_usage['total']:,}")
    if msg.response_time:
        metadata.append(f"Time: {msg.response_time:.2f}s")

    if metadata:
        container.markdown("---")
        container.markdown(" | ".join(metadata))


def chatmessage_view(
    messages: list[ChatMessage[Any]], container: DeltaGenerator | None = None
):
    """Display a list of chat messages with tool calls and metadata.

    Args:
        messages: List of messages to display
        container: Optional streamlit container to use (defaults to st)
    """
    st_container = container or st

    for msg in messages:
        role = "user" if msg.role == "user" else "assistant"
        with st_container.chat_message(role):
            render_message_content(msg, st_container)  # type: ignore


if __name__ == "__main__":
    from llmling_agent import ToolCallInfo

    from utils import run

    tool_calls = [
        ToolCallInfo(tool_name=f"test_{i}", result="result!", agent_name="agent", args={})
        for i in range(3)
    ]
    message = ChatMessage("test", role="user", tool_calls=tool_calls)
    run(lambda: chatmessage_view([message]))
