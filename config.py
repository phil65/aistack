"""Configuration and constants for the Streamlit application."""

from __future__ import annotations

from llmling_agent import Tool
from llmling_agent_tools import serper_search
from llmling_agent_tools.jira_tool import jira_tools
from pydantic import BaseModel, ConfigDict


search_tool = Tool.from_callable(serper_search.SerperTool().search)
create_issue_tool = Tool.from_callable(jira_tools.create_issue)
search_jira_tool = Tool.from_callable(jira_tools.search_for_issues)


class FormData(BaseModel):
    """Data structure for form inputs."""

    title: str = ""
    """Titel des Projekts"""

    description: str = ""
    """Beschreibung des Projekts"""

    requirements: str = ""
    """Anforderungen des Projekts"""

    constraints: str = ""
    """Einschränkungen des Projekts"""

    additional_info: str = ""
    """Weitere relevante Informationen"""

    model_config = ConfigDict(use_attribute_docstrings=True)

    def format_context(self) -> str:
        """Format the form data into a context string."""
        return (
            "Projektinformationen:\n\n"
            f"Titel: {self.title}\n\n"
            f"Beschreibung:\n{self.description}\n\n"
            f"Anforderungen:\n{self.requirements}\n\n"
            f"Einschränkungen:\n{self.constraints}\n\n"
            f"Weitere Informationen:\n{self.additional_info}"
        )


# Field descriptions for the form - matches FormData fields
FORM_FIELDS = {
    "title": "Titel des Projekts",
    "description": "Beschreibung",
    "requirements": "Anforderungen",
    "constraints": "Einschränkungen",
    "additional_info": "Weitere Informationen",
}
