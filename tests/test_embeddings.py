"""Unit tests for RAG embeddings."""

import unittest
from docuagent.rag.embeddings import dense_embeddings, sparse_embeddings


class TestEmbeddings(unittest.TestCase):
    def test_dense_embeddings_dimension(self):
        vec = dense_embeddings.embed_query("healthcheck query")
        self.assertIsInstance(vec, list)
        self.assertEqual(len(vec), 384)

    def test_sparse_embeddings_format(self):
        sparse_vec = sparse_embeddings.embed_query("healthcheck query")
        self.assertTrue(hasattr(sparse_vec, "indices"))
        self.assertGreater(len(sparse_vec.indices), 0)


if __name__ == "__main__":
    unittest.main()
