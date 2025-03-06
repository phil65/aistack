"""Model selector component for streamlit applications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import streamlit as st

from utils import run


if TYPE_CHECKING:
    from collections.abc import Sequence

    from llmling_agent_config.task import AnyAgent
    from tokonomics.model_discovery import ModelInfo, ProviderType


def model_selector(
    *,
    agent: AnyAgent[Any, Any],
    providers: Sequence[ProviderType] | None = None,
    expanded: bool = True,
) -> ModelInfo | None:
    """Render a model selector with provider and model dropdowns.

    This component uses the agent's current model configuration and
    updates the agent directly when selections change.

    Args:
        agent: Agent object with set_model method and model_name attribute
        providers: List of providers to show models from
        expanded: Whether to expand the model details by default

    Returns:
        Selected model info or None if not selected
    """
    # Fetch models
    from tokonomics.model_discovery import get_all_models_sync

    models = get_all_models_sync(providers=providers)

    # Get unique providers from models
    available_providers = sorted({model.provider for model in models})

    # Get current model info to set initial selections
    current_model_id = agent.model_name
    current_model = None
    current_provider = None

    if current_model_id:
        current_model = next(
            (m for m in models if m.pydantic_ai_id == current_model_id),
            None,
        )
        if current_model:
            current_provider = current_model.provider

    # Provider selection
    if len(available_providers) > 1:
        # Use current provider if found, otherwise first provider
        default_provider_idx = (
            available_providers.index(current_provider)
            if current_provider in available_providers
            else 0
        )

        selected_provider = st.selectbox(
            "Provider",
            options=available_providers,
            index=default_provider_idx,
        )
    else:
        selected_provider = available_providers[0]

    # Filter models by selected provider
    provider_models = [m for m in models if m.provider == selected_provider]
    model_names = [m.name for m in provider_models]

    # Determine initial model index
    default_model_idx = 0
    if current_model and current_model.provider == selected_provider:
        try:
            default_model_idx = model_names.index(current_model.name)
        except ValueError:
            default_model_idx = 0

    # Model selection
    selected_name = st.selectbox(
        "Model",
        options=model_names,
        index=default_model_idx,
    )

    # Find selected model info
    selected_model = next(
        (m for m in provider_models if m.name == selected_name),
        None,
    )

    # Show model details in expander
    if selected_model:
        with st.expander("Model Details", expanded=expanded):
            st.markdown(selected_model.format())

        # Update agent model if it changed
        if selected_model.pydantic_ai_id != current_model_id:
            agent.set_model(selected_model.pydantic_ai_id)

    return selected_model


if __name__ == "__main__":
    run(model_selector)
