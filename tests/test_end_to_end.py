"""
End-to-end tests for the document pipeline.
"""

import unittest
import tempfile
from pathlib import Path
from src.core.models import Chunk
from src.document.document_loader import DocumentLoader
from conftest import TestRetriever


class TestDocumentPipeline(unittest.TestCase):
    """Test complete document pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()
    
    def test_document_loader_with_mock_documents(self):
        """Test document loader with in-memory mock."""
        loader = DocumentLoader(index_name="test_index")
        
        # Manually add some pages and chunks (simulating what PDF parser would do)
        from src.core.models import Document, DocumentType
        
        doc = Document(
            document_id="test_doc_1",
            file_name="test.pdf",
            file_path="/tmp/test.pdf",
            document_type=DocumentType.PDF,
            total_pages=2,
        )
        
        loader.documents[doc.document_id] = doc
        
        # Add chunks
        chunks = [
            Chunk("c1", doc.document_id, 0, "Machine learning is a subset of artificial intelligence."),
            Chunk("c2", doc.document_id, 0, "Supervised learning requires labeled training data."),
            Chunk("c3", doc.document_id, 1, "Deep learning uses neural networks with multiple layers."),
        ]
        loader.chunks.extend(chunks)
        loader.metadata.total_documents = 1
        loader.metadata.total_chunks = len(chunks)
        
        # Test document info retrieval
        info = loader.get_document_info("test_doc_1")
        self.assertEqual(info['document_id'], "test_doc_1")
        self.assertEqual(info['total_chunks'], 3)
        
        # Test index stats
        stats = loader.get_index_stats()
        self.assertEqual(stats['total_documents'], 1)
        self.assertEqual(stats['total_chunks'], 3)
    
    def test_retriever_on_mock_index(self):
        """Test retriever on mock document index."""
        from src.core.models import Document, DocumentType
        
        # Create mock documents and chunks
        doc = Document(
            document_id="course_101",
            file_name="ML_Basics.pdf",
            file_path="/tmp/ML.pdf",
            document_type=DocumentType.PDF,
            total_pages=10,
        )
        
        chunks = [
            Chunk("c1", doc.document_id, 0, "Supervised learning requires labeled examples. Classification and regression are common tasks."),
            Chunk("c2", doc.document_id, 1, "Unsupervised learning finds patterns without labels. Clustering and dimensionality reduction are key techniques."),
            Chunk("c3", doc.document_id, 2, "Neural networks consist of interconnected nodes organized in layers."),
            Chunk("c4", doc.document_id, 3, "Deep learning uses neural networks with many hidden layers to learn complex representations."),
            Chunk("c5", doc.document_id, 4, "Overfitting occurs when a model memorizes training data rather than learning general patterns."),
        ]
        
        # Create retriever
        retriever = TestRetriever(chunks, {"course_101": doc})
        
        # Test basic search
        results = retriever.search("supervised learning", top_k=3)
        
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 3)
        
        # First result should be about supervised learning
        self.assertIn("supervised", results[0].chunk.text.lower())
    
    def test_end_to_end_flow(self):
        """Test end-to-end search flow."""
        from src.core.models import Document, DocumentType
        
        # Simulate loading a course
        doc = Document(
            document_id="statistics_201",
            file_name="Stats_for_Business.pdf",
            file_path="/tmp/stats.pdf",
            document_type=DocumentType.PDF,
            total_pages=15,
        )
        
        chunks = [
            Chunk("c1", doc.document_id, 0, "Descriptive statistics summarize data using measures like mean, median, and standard deviation."),
            Chunk("c2", doc.document_id, 1, "Inferential statistics uses samples to make inferences about populations."),
            Chunk("c3", doc.document_id, 2, "A hypothesis test compares observed data against a null hypothesis."),
            Chunk("c4", doc.document_id, 3, "Statistical significance is determined by p-values and significance levels."),
            Chunk("c5", doc.document_id, 4, "Regression models the relationship between variables using linear or non-linear equations."),
        ]
        
        # Create retriever and search
        retriever = TestRetriever(chunks, {"statistics_201": doc})
        
        # Simulate teacher query
        query = "How do I explain hypothesis testing to students?"
        results = retriever.search(query, top_k=3)
        
        # Verify results
        self.assertGreater(len(results), 0)
        
        # Print results for manual inspection
        print(f"\nQuery: {query}")
        print(f"Results from {doc.file_name}:")
        for result in results:
            print(f"  Page {result.chunk.page_number}: {result.chunk.text[:80]}...")
            print(f"  Score: {result.score:.3f}\n")


if __name__ == '__main__':
    unittest.main()
