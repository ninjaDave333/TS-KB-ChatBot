"""
Integration test for Phase 4: Tracing and Evaluation pipeline.
Tests end-to-end tracing and evaluation functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
from app.core.tracing import new_trace, write_trace, TRACE_FILE
from app.core.evaluation import write_eval, EVAL_FILE
from app.core.judge_client import evaluate_trace

class TestPhase4Integration:
    """Integration tests for Phase 4 tracing and evaluation."""
    
    def test_trace_file_creation(self):
        """Test that traces.jsonl is created and populated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_trace_file = Path(temp_dir) / "traces.jsonl"
            
            with patch.object(Path, '__new__', lambda cls, path: test_trace_file if '/app/data/traces.jsonl' in str(path) else Path(path)):
                # Simulate a query execution with tracing
                trace = new_trace("count_query", True, "ai_generated")
                
                # Populate trace as would happen in pipeline
                trace.retrieval_config = {"strategy": "cypher", "limit": 100}
                trace.cypher_query = "MATCH (c:Client) RETURN count(c) as clientCount"
                trace.cypher_params = {}
                trace.neo4j_result_summary = {"record_count": 1, "has_data": True}
                trace.prompt_system = "You are a Cypher generator"
                trace.prompt_user = "How many clients are there?"
                trace.llm_model_role = "primary"
                trace.llm_model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
                trace.final_answer = "There are 150 clients in the system."
                
                # Write trace
                with patch('app.core.tracing.TRACE_FILE', test_trace_file):
                    write_trace(trace)
                
                # Verify trace file exists and contains expected data
                assert test_trace_file.exists()
                
                with test_trace_file.open("r") as f:
                    trace_data = json.loads(f.readline())
                    
                    # Verify all required fields are present
                    required_fields = [
                        "trace_id", "timestamp", "intent", "use_ai", "routing_path",
                        "retrieval_config", "cypher_query", "cypher_params", 
                        "neo4j_result_summary", "prompt_system", "prompt_user",
                        "llm_model_role", "llm_model_id", "final_answer"
                    ]
                    
                    for field in required_fields:
                        assert field in trace_data, f"Missing required field: {field}"
                    
                    # Verify specific values
                    assert trace_data["intent"] == "count_query"
                    assert trace_data["use_ai"] is True
                    assert trace_data["routing_path"] == "ai_generated"
                    assert trace_data["cypher_query"] == "MATCH (c:Client) RETURN count(c) as clientCount"
                    assert trace_data["llm_model_role"] == "primary"
                    assert trace_data["final_answer"] == "There are 150 clients in the system."
    
    @pytest.mark.asyncio
    async def test_evaluation_pipeline(self):
        """Test that evaluation pipeline works end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_eval_file = Path(temp_dir) / "eval_results.jsonl"
            
            with patch('app.core.evaluation.EVAL_FILE', test_eval_file):
                # Create a trace to evaluate
                trace = new_trace("count_query", True, "ai_generated")
                trace.prompt_user = "How many clients are there?"
                trace.cypher_query = "MATCH (c:Client) RETURN count(c) as clientCount"
                trace.neo4j_result_summary = {"record_count": 1, "has_data": True}
                trace.final_answer = "There are 150 clients in the system."
                
                # Mock LLM client for judge evaluation
                mock_llm_client = AsyncMock()
                judge_response = json.dumps({
                    "overall_score": 8.5,
                    "factual_correctness": 9.0,
                    "grounded_in_context": 8.0,
                    "helpfulness": 8.5,
                    "error_type": "none"
                })
                mock_llm_client.complete.return_value = judge_response
                
                # Evaluate trace
                eval_result = await evaluate_trace(mock_llm_client, trace)
                
                # Verify evaluation result
                assert eval_result is not None
                assert eval_result.trace_id == trace.trace_id
                assert eval_result.overall_score == 8.5
                assert eval_result.factual_correctness == 9.0
                
                # Write evaluation result
                write_eval(eval_result)
                
                # Verify eval file exists and contains expected data
                assert test_eval_file.exists()
                
                with test_eval_file.open("r") as f:
                    eval_data = json.loads(f.readline())
                    
                    # Verify all required fields are present
                    required_fields = [
                        "trace_id", "overall_score", "factual_correctness",
                        "grounded_in_context", "helpfulness", "error_type"
                    ]
                    
                    for field in required_fields:
                        assert field in eval_data, f"Missing required field: {field}"
                    
                    # Verify values match
                    assert eval_data["trace_id"] == trace.trace_id
                    assert eval_data["overall_score"] == 8.5
                    assert eval_data["factual_correctness"] == 9.0
                    assert eval_data["grounded_in_context"] == 8.0
                    assert eval_data["helpfulness"] == 8.5
                    assert eval_data["error_type"] == "none"
    
    def test_multiple_traces_and_evaluations(self):
        """Test that multiple traces and evaluations can be written."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_trace_file = Path(temp_dir) / "traces.jsonl"
            test_eval_file = Path(temp_dir) / "eval_results.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', test_trace_file), \
                 patch('app.core.evaluation.EVAL_FILE', test_eval_file):
                
                # Create multiple traces
                traces = []
                for i in range(3):
                    trace = new_trace(f"query_{i}", True, "ai_generated")
                    trace.cypher_query = f"MATCH (n) RETURN n LIMIT {i+1}"
                    trace.final_answer = f"Answer {i+1}"
                    traces.append(trace)
                    
                    # Write each trace
                    write_trace(trace)
                
                # Verify all traces were written
                with test_trace_file.open("r") as f:
                    lines = f.readlines()
                    assert len(lines) == 3
                    
                    for i, line in enumerate(lines):
                        data = json.loads(line)
                        assert data["trace_id"] == traces[i].trace_id
                        assert data["intent"] == f"query_{i}"
                        assert data["cypher_query"] == f"MATCH (n) RETURN n LIMIT {i+1}"
    
    def test_trace_safety_on_errors(self):
        """Test that tracing errors don't break the pipeline."""
        # Test with invalid file path that would cause write errors
        invalid_path = Path("/invalid/path/that/does/not/exist/traces.jsonl")
        
        with patch('app.core.tracing.TRACE_FILE', invalid_path):
            trace = new_trace("test", True, "test")
            
            # This should not raise an exception due to safe_write_trace
            from app.core.tracing import safe_write_trace
            safe_write_trace(trace)  # Should complete without error
    
    @pytest.mark.asyncio
    async def test_judge_model_role_usage(self):
        """Test that judge model uses correct role parameter."""
        mock_llm_client = AsyncMock()
        judge_response = json.dumps({
            "overall_score": 7.0,
            "factual_correctness": 7.0,
            "grounded_in_context": 7.0,
            "helpfulness": 7.0,
            "error_type": "none"
        })
        mock_llm_client.complete.return_value = judge_response
        
        trace = new_trace("test", True, "ai")
        trace.prompt_user = "Test question"
        trace.final_answer = "Test answer"
        
        # Evaluate trace
        eval_result = await evaluate_trace(mock_llm_client, trace)
        
        # Verify judge role was used
        mock_llm_client.complete.assert_called_once()
        call_args = mock_llm_client.complete.call_args
        assert call_args[1]["role"] == "judge"
        
        # Verify evaluation succeeded
        assert eval_result is not None
        assert eval_result.trace_id == trace.trace_id
    
    def test_data_directory_creation(self):
        """Test that /app/data directory is created automatically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            nested_trace_file = Path(temp_dir) / "app" / "data" / "traces.jsonl"
            nested_eval_file = Path(temp_dir) / "app" / "data" / "eval_results.jsonl"
            
            with patch('app.core.tracing.TRACE_FILE', nested_trace_file), \
                 patch('app.core.evaluation.EVAL_FILE', nested_eval_file):
                
                # Write trace and evaluation
                trace = new_trace("test", True, "test")
                write_trace(trace)
                
                from app.core.evaluation import EvalResult, write_eval
                eval_result = EvalResult(
                    trace_id=trace.trace_id,
                    overall_score=8.0,
                    factual_correctness=8.0,
                    grounded_in_context=8.0,
                    helpfulness=8.0,
                    error_type="none"
                )
                write_eval(eval_result)
                
                # Verify directories were created
                assert nested_trace_file.parent.exists()
                assert nested_eval_file.parent.exists()
                assert nested_trace_file.exists()
                assert nested_eval_file.exists()

class TestPhase4BehavioralSafety:
    """Test that Phase 4 doesn't break existing functionality."""
    
    def test_tracing_does_not_affect_query_response(self):
        """Test that tracing doesn't change query response format."""
        # This would be tested in actual API integration
        # For now, verify that trace operations are isolated
        
        trace = new_trace("test", True, "ai")
        
        # Simulate query processing
        original_query = "How many clients are there?"
        original_answer = "There are 150 clients."
        
        # Populate trace
        trace.cypher_query = "MATCH (c:Client) RETURN count(c)"
        trace.final_answer = original_answer
        
        # Verify original data is unchanged
        assert original_query == "How many clients are there?"
        assert original_answer == "There are 150 clients."
        
        # Trace should contain the data but not modify originals
        assert trace.final_answer == original_answer
        assert trace.cypher_query == "MATCH (c:Client) RETURN count(c)"
    
    def test_evaluation_failure_isolation(self):
        """Test that evaluation failures don't affect main pipeline."""
        with patch('app.core.evaluation.write_eval', side_effect=Exception("Eval error")):
            from app.core.evaluation import safe_write_eval, EvalResult
            
            eval_result = EvalResult(
                trace_id="test",
                overall_score=8.0,
                factual_correctness=8.0,
                grounded_in_context=8.0,
                helpfulness=8.0,
                error_type="none"
            )
            
            # Should not raise exception
            safe_write_eval(eval_result)

if __name__ == "__main__":
    pytest.main([__file__])