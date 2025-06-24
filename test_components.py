import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from internet_search import duckduckgo_search, wikipedia_summary
from deepseek_api import generate_expert_fallback
from vector_search import get_pdf_context
from ollama_chat import generate_fallback_response

def test_duckduckgo_search():
    """Test DuckDuckGo search functionality"""
    results = duckduckgo_search("artificial intelligence", max_results=2)
    assert isinstance(results, list)
    # Should return results or empty list (not None)
    assert results is not None

def test_wikipedia_summary():
    """Test Wikipedia summary functionality"""
    result = wikipedia_summary("Python programming language")
    assert isinstance(result, str)
    # Should return string (empty if not found)
    assert result is not None

def test_expert_fallback():
    """Test expert analysis fallback"""
    result = generate_expert_fallback("artificial intelligence")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Expert Analysis:" in result

def test_ollama_fallback():
    """Test Ollama fallback response"""
    result = generate_fallback_response("Hello")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "🚀" in result

def test_pdf_context_no_docs():
    """Test PDF context when no documents available"""
    result = get_pdf_context("test query")
    assert isinstance(result, str)
    # Should handle gracefully when no docs available

if __name__ == '__main__':
    pytest.main([__file__])
