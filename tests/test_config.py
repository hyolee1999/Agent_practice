"""Unit tests for configuration layer."""

import unittest
from docuagent.config.settings import settings


class TestConfig(unittest.TestCase):
    def test_settings_loaded(self):
        self.assertEqual(settings.app_name, "DocuAgent AI")
        self.assertIsNotNone(settings.qdrant_url)
        self.assertEqual(settings.dense_embedding_model, "BAAI/bge-small-en-v1.5")
        self.assertEqual(settings.sparse_embedding_model, "Qdrant/bm25")


if __name__ == "__main__":
    unittest.main()
