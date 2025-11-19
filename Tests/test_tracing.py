"""
Unit tests for RAG pipeline tracing functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from app.core.tracing import RagTrace, new_trace, write_trace, safe_write_trace

class TestRagTrace:
    """Test RagTrace dataclass functionality."""
    
    def test_new_trace_creates_valid_trace(self):
        """Test that new_trace creates a RagTrace with expected defaults."""
        trace = new_trace(intent="test_intent", use_ai=True, routing_path="ai_generated")
        
        assert trace.intent == "test_intent"
        assert trace.use_ai is True
        assert trace.routing_path == "ai_generated"
        assert trace.trace_id is not None
        assert trace.timestamp is not None
        assert trace.retrieval_config == {}
        assert trace.cypher_query is None
        assert trace.final_answer is None
    
    def test_new_trace_generates_unique_ids(self):
        """Test that each new trace gets a unique ID."""
        import time
        trace1 = new_trace("intent1", True, "path1")
        time.sleep(0.001)  # Ensure different timestamps
        trace2 = new_trace("intent2", False, "path2")
        
        assert trace1.trace_id != trace2.trace_id
        assert trace1.timestamp != trace2.timestamp
    
    def test_trace_can_be_populated(self):
        """Test that trace fields can be populated after creation."""
        trace = new_trace("test", True, "ai")
        
        trace.cypher_query = "MATCH (n) RETURN n"
        trace.cypher_params = {"limit": 10}
        trace.neo4j_result_summary = {"record_count": 5}
        trace.final_answer = "Test answer"
        
        assert trace.cypher_query == "MATCH (n) RETURN n"
        assert trace.cypher_params == {"limit": 10}
        assert trace.neo4j_result_summary == {"record_count": 5}
        assert trace.final_answer == "Test answer"

class TestTraceWriting:
    """Test trace writing functionality."""
    
    def test_write_trace_creates_valid_jsonl(self):
        """Test that write_trace creates valid JSONL format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the TRACE_FILE path
            test_file = Path(temp_dir) / "test_traces.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', test_file):
                trace = new_trace("test_intent", True, "test_path")
                trace.cypher_query = "MATCH (n) RETURN n"
                trace.final_answer = "Test answer"
                
                write_trace(trace)
                
                # Verify file was created and contains valid JSON
                assert test_file.exists()
                
                with test_file.open("r") as f:
                    line = f.readline().strip()
                    data = json.loads(line)
                    
                    assert data["trace_id"] == trace.trace_id
                    assert data["intent"] == "test_intent"
                    assert data["use_ai"] is True
                    assert data["routing_path"] == "test_path"
                    assert data["cypher_query"] == "MATCH (n) RETURN n"
                    assert data["final_answer"] == "Test answer"
    
    def test_write_trace_appends_multiple_traces(self):
        """Test that multiple traces are appended to the same file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_traces.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', test_file):
                trace1 = new_trace("intent1", True, "path1")
                trace2 = new_trace("intent2", False, "path2")
                
                write_trace(trace1)
                write_trace(trace2)
                
                # Verify both traces are in file
                with test_file.open("r") as f:
                    lines = f.readlines()
                    
                    assert len(lines) == 2
                    
                    data1 = json.loads(lines[0])
                    data2 = json.loads(lines[1])
                    
                    assert data1["trace_id"] == trace1.trace_id
                    assert data2["trace_id"] == trace2.trace_id
    
    def test_safe_write_trace_handles_errors(self):
        """Test that safe_write_trace doesn't raise exceptions."""
        # Mock write_trace to raise an exception
        with patch('app.core.tracing.write_trace', side_effect=Exception("Test error")):
            trace = new_trace("test", True, "test")
            
            # Should not raise exception
            safe_write_trace(trace)
    
    def test_write_trace_creates_directory(self):
        """Test that write_trace creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            test_file = Path(temp_dir) / "nested" / "dir" / "traces.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', test_file):
                trace = new_trace("test", True, "test")
                
                write_trace(trace)
                
                # Verify directory was created and file exists
                assert test_file.parent.exists()
                assert test_file.exists()

class TestTraceIntegration:
    """Test trace integration scenarios."""
    
    def test_complete_trace_lifecycle(self):
        """Test a complete trace from creation to writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "integration_traces.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', test_file):
                # Create and populate trace as would happen in pipeline
                trace = new_trace("count_query", True, "ai_generated")
                
                # Simulate pipeline steps
                trace.retrieval_config = {"strategy": "cypher", "limit": 100}
                trace.cypher_query = "MATCH (c:Client) RETURN count(c) as clientCount"
                trace.cypher_params = {}
                trace.neo4j_result_summary = {"record_count": 1, "has_data": True}
                trace.prompt_system = "You are a Cypher generator"
                trace.prompt_user = "How many clients are there?"
                trace.llm_model_role = "primary"
                trace.llm_model_id = "claude-sonnet-4"
                trace.final_answer = "There are 150 clients in the system."
                
                # Write trace
                safe_write_trace(trace)
                
                # Verify complete trace was written
                with test_file.open("r") as f:
                    data = json.loads(f.readline())
                    
                    assert data["intent"] == "count_query"
                    assert data["use_ai"] is True
                    assert data["routing_path"] == "ai_generated"
                    assert data["retrieval_config"]["strategy"] == "cypher"
                    assert data["cypher_query"] == "MATCH (c:Client) RETURN count(c) as clientCount"
                    assert data["neo4j_result_summary"]["record_count"] == 1
                    assert data["llm_model_role"] == "primary"
                    assert data["llm_model_id"] == "claude-sonnet-4"
                    assert data["final_answer"] == "There are 150 clients in the system."

if __name__ == "__main__":
    pytest.main([__file__])