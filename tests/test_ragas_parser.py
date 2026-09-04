"""Unit tests for JSON extraction from markdown code fences."""

import unittest
from ragas.prompt.utils import extract_json


class TestRagasParser(unittest.TestCase):
    def test_extract_json_from_markdown_fence(self):
        fenced_text = '```json\n{"statements": ["Fact 1", "Fact 2"]}\n```'
        extracted = extract_json(fenced_text)
        self.assertEqual(extracted.strip(), '{"statements": ["Fact 1", "Fact 2"]}')

    def test_extract_json_from_raw_json(self):
        raw_text = '{"statements": ["Fact 1", "Fact 2"]}'
        extracted = extract_json(raw_text)
        self.assertEqual(extracted.strip(), raw_text)

    def test_vertexai_compatibility_shim(self):
        """Verify that Ragas Issue #2745 legacy imports resolve cleanly."""
        import docuagent.observability.metrics  # triggers shim initialization
        from langchain_community.chat_models.vertexai import ChatVertexAI
        from langchain_community.llms import VertexAI

        self.assertIsNotNone(ChatVertexAI)
        self.assertIsNotNone(VertexAI)


if __name__ == "__main__":
    unittest.main()
