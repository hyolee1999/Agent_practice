"""Unit tests for pure Python agent factory (verifying no Streamlit dependency)."""

import unittest
from langchain_core.tools import tool
from docuagent.agent.factory import create_rag_agent


@tool
def mock_retriever_tool(query: str) -> str:
    """Mock tool for testing."""
    return "Sample document context"


class TestAgentFactory(unittest.TestCase):
    def test_create_agent_without_streamlit(self):
        # Verify creating an agent works cleanly in pure Python
        agent = create_rag_agent(tools=[mock_retriever_tool], init_eval_metrics=False)
        self.assertIsNotNone(agent)
        self.assertTrue(hasattr(agent, "invoke"))


if __name__ == "__main__":
    unittest.main()
