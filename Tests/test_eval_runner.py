"""
Unit tests for evaluation runner daemon.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.monitoring.eval_runner import EvalRunner
from app.core.tracing import RagTrace
from app.core.evaluation import EvalResult

class TestEvalRunner:
    """Test evaluation runner functionality."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client."""
        return AsyncMock()
    
    @pytest.fixture
    def eval_runner(self, mock_llm_client):
        """Create evaluation runner with mock LLM client."""
        return EvalRunner(mock_llm_client)
    
    @pytest.fixture
    def sample_traces(self):
        """Create sample traces for testing."""
        return [
            {
                "trace_id": "trace-001",
                "timestamp": "2025-11-19T10:00:00Z",
                "intent": "count_query",
                "use_ai": True,
                "routing_path": "ai_generated",
                "retrieval_config": {},
                "cypher_query": "MATCH (c:Client) RETURN count(c)",
                "cypher_params": {},
                "neo4j_result_summary": {"record_count": 1},
                "prompt_system": "System prompt",
                "prompt_user": "How many clients?",
                "llm_model_role": "primary",
                "llm_model_id": "claude-sonnet-4",
                "final_answer": "There are 150 clients."
            },
            {
                "trace_id": "trace-002",
                "timestamp": "2025-11-19T11:00:00Z",
                "intent": "list_query",
                "use_ai": True,
                "routing_path": "ai_generated",
                "retrieval_config": {},
                "cypher_query": "MATCH (c:Client) RETURN c.name",
                "cypher_params": {},
                "neo4j_result_summary": {"record_count": 5},
                "prompt_system": "System prompt",
                "prompt_user": "List clients",
                "llm_model_role": "primary",
                "llm_model_id": "claude-sonnet-4",
                "final_answer": "Here are the clients: A, B, C, D, E"
            }
        ]
    
    @pytest.fixture
    def sample_evaluations(self):
        """Create sample evaluations for testing."""
        return [
            {
                "trace_id": "trace-001",
                "overall_score": 8.5,
                "factual_correctness": 9.0,
                "grounded_in_context": 8.0,
                "helpfulness": 8.5,
                "error_type": "none"
            }
        ]
    
    def test_load_existing_evaluations_empty(self, eval_runner):
        """Test loading evaluations when file doesn't exist."""
        with patch('app.monitoring.eval_runner.EVAL_FILE') as mock_file:
            mock_file.exists.return_value = False
            
            result = eval_runner.load_existing_evaluations()
            
            assert result == set()
    
    def test_load_existing_evaluations_with_data(self, eval_runner, sample_evaluations):
        """Test loading existing evaluations from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for eval_data in sample_evaluations:
                f.write(json.dumps(eval_data) + "\n")
            temp_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.EVAL_FILE', temp_path):
                result = eval_runner.load_existing_evaluations()
                
                assert result == {"trace-001"}
        finally:
            temp_path.unlink()
    
    def test_load_traces_no_file(self, eval_runner):
        """Test loading traces when file doesn't exist."""
        with patch('app.monitoring.eval_runner.TRACE_FILE') as mock_file:
            mock_file.exists.return_value = False
            
            result = eval_runner.load_traces()
            
            assert result == []
    
    def test_load_traces_with_data(self, eval_runner, sample_traces):
        """Test loading traces from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for trace_data in sample_traces:
                f.write(json.dumps(trace_data) + "\n")
            temp_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.TRACE_FILE', temp_path):
                result = eval_runner.load_traces()
                
                assert len(result) == 2
                assert result[0].trace_id == "trace-001"
                assert result[1].trace_id == "trace-002"
        finally:
            temp_path.unlink()
    
    def test_load_traces_with_max_limit(self, eval_runner, sample_traces):
        """Test loading traces with max_traces limit."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for trace_data in sample_traces:
                f.write(json.dumps(trace_data) + "\n")
            temp_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.TRACE_FILE', temp_path):
                result = eval_runner.load_traces(max_traces=1)
                
                assert len(result) == 1
                assert result[0].trace_id == "trace-001"
        finally:
            temp_path.unlink()
    
    def test_load_traces_with_intent_filter(self, eval_runner, sample_traces):
        """Test loading traces with intent filter."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for trace_data in sample_traces:
                f.write(json.dumps(trace_data) + "\n")
            temp_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.TRACE_FILE', temp_path):
                result = eval_runner.load_traces(intent_filter="count_query")
                
                assert len(result) == 1
                assert result[0].intent == "count_query"
        finally:
            temp_path.unlink()
    
    def test_load_traces_with_since_filter(self, eval_runner, sample_traces):
        """Test loading traces with since timestamp filter."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for trace_data in sample_traces:
                f.write(json.dumps(trace_data) + "\n")
            temp_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.TRACE_FILE', temp_path):
                result = eval_runner.load_traces(since="2025-11-19T10:30:00Z")
                
                assert len(result) == 1
                assert result[0].trace_id == "trace-002"
        finally:
            temp_path.unlink()
    
    def test_filter_unevaluated_traces(self, eval_runner):
        """Test filtering out already evaluated traces."""
        traces = [
            RagTrace(trace_id="trace-001", timestamp="2025-11-19T10:00:00Z", 
                    intent="test", use_ai=True, routing_path="ai",
                    retrieval_config={}, cypher_query=None, cypher_params={},
                    neo4j_result_summary={}, prompt_system=None, prompt_user=None,
                    llm_model_role=None, llm_model_id=None, final_answer=None),
            RagTrace(trace_id="trace-002", timestamp="2025-11-19T11:00:00Z",
                    intent="test", use_ai=True, routing_path="ai",
                    retrieval_config={}, cypher_query=None, cypher_params={},
                    neo4j_result_summary={}, prompt_system=None, prompt_user=None,
                    llm_model_role=None, llm_model_id=None, final_answer=None)
        ]
        evaluated_ids = {"trace-001"}
        
        result = eval_runner.filter_unevaluated_traces(traces, evaluated_ids)
        
        assert len(result) == 1
        assert result[0].trace_id == "trace-002"
    
    @pytest.mark.asyncio
    async def test_evaluate_batch_success(self, eval_runner):
        """Test successful batch evaluation."""
        traces = [
            RagTrace(trace_id="trace-001", timestamp="2025-11-19T10:00:00Z",
                    intent="test", use_ai=True, routing_path="ai",
                    retrieval_config={}, cypher_query="MATCH (n) RETURN n", cypher_params={},
                    neo4j_result_summary={}, prompt_system="sys", prompt_user="user",
                    llm_model_role="primary", llm_model_id="claude", final_answer="answer")
        ]
        
        mock_eval_result = EvalResult(
            trace_id="trace-001",
            overall_score=8.5,
            factual_correctness=9.0,
            grounded_in_context=8.0,
            helpfulness=8.5,
            error_type="none"
        )
        
        with patch('app.monitoring.eval_runner.evaluate_trace', return_value=mock_eval_result) as mock_evaluate, \
             patch('app.monitoring.eval_runner.write_eval') as mock_write:
            
            result = await eval_runner.evaluate_batch(traces)
            
            assert len(result) == 1
            assert result[0].trace_id == "trace-001"
            mock_evaluate.assert_called_once()
            mock_write.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_batch_with_errors(self, eval_runner):
        """Test batch evaluation with some failures."""
        traces = [
            RagTrace(trace_id="trace-001", timestamp="2025-11-19T10:00:00Z",
                    intent="test", use_ai=True, routing_path="ai",
                    retrieval_config={}, cypher_query="MATCH (n) RETURN n", cypher_params={},
                    neo4j_result_summary={}, prompt_system="sys", prompt_user="user",
                    llm_model_role="primary", llm_model_id="claude", final_answer="answer"),
            RagTrace(trace_id="trace-002", timestamp="2025-11-19T11:00:00Z",
                    intent="test", use_ai=True, routing_path="ai",
                    retrieval_config={}, cypher_query="MATCH (n) RETURN n", cypher_params={},
                    neo4j_result_summary={}, prompt_system="sys", prompt_user="user",
                    llm_model_role="primary", llm_model_id="claude", final_answer="answer")
        ]
        
        mock_eval_result = EvalResult(
            trace_id="trace-001",
            overall_score=8.5,
            factual_correctness=9.0,
            grounded_in_context=8.0,
            helpfulness=8.5,
            error_type="none"
        )
        
        def mock_evaluate_side_effect(llm_client, trace):
            if trace.trace_id == "trace-001":
                return mock_eval_result
            else:
                raise Exception("Evaluation failed")
        
        with patch('app.monitoring.eval_runner.evaluate_trace', side_effect=mock_evaluate_side_effect) as mock_evaluate, \
             patch('app.monitoring.eval_runner.write_eval') as mock_write:
            
            result = await eval_runner.evaluate_batch(traces)
            
            assert len(result) == 1  # Only successful evaluation
            assert result[0].trace_id == "trace-001"
            assert mock_evaluate.call_count == 2  # Both traces attempted
            mock_write.assert_called_once()  # Only successful one written
    
    def test_generate_metrics_summary_no_file(self, eval_runner):
        """Test metrics summary generation when no eval file exists."""
        with patch('app.monitoring.eval_runner.EVAL_FILE') as mock_file:
            mock_file.exists.return_value = False
            
            result = eval_runner.generate_metrics_summary()
            
            assert "error" in result
    
    def test_generate_metrics_summary_with_data(self, eval_runner, sample_evaluations):
        """Test metrics summary generation with evaluation data."""
        # Create eval file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for eval_data in sample_evaluations:
                f.write(json.dumps(eval_data) + "\n")
            eval_path = Path(f.name)
        
        # Create trace file for intent mapping
        trace_data = {
            "trace_id": "trace-001",
            "intent": "count_query",
            "timestamp": "2025-11-19T10:00:00Z"
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(json.dumps(trace_data) + "\n")
            trace_path = Path(f.name)
        
        try:
            with patch('app.monitoring.eval_runner.EVAL_FILE', eval_path), \
                 patch('app.monitoring.eval_runner.TRACE_FILE', trace_path):
                
                result = eval_runner.generate_metrics_summary()
                
                assert "generated_at" in result
                assert "global" in result
                assert "by_intent" in result
                
                # Check global metrics
                global_metrics = result["global"]
                assert global_metrics["total_evals"] == 1
                assert global_metrics["avg_overall_score"] == 8.5
                
                # Check intent metrics
                assert "count_query" in result["by_intent"]
                intent_metrics = result["by_intent"]["count_query"]
                assert intent_metrics["eval_count"] == 1
                assert intent_metrics["avg_overall_score"] == 8.5
                assert "error_type_distribution" in intent_metrics
                
        finally:
            eval_path.unlink()
            trace_path.unlink()
    
    def test_write_summary(self, eval_runner):
        """Test writing metrics summary to file."""
        summary = {
            "generated_at": "2025-11-19T12:00:00Z",
            "global": {"total_evals": 1, "avg_overall_score": 8.5}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = Path(temp_dir) / "eval_summary.json"
            
            with patch('app.monitoring.eval_runner.SUMMARY_FILE', summary_path):
                eval_runner.write_summary(summary)
                
                assert summary_path.exists()
                
                with summary_path.open("r") as f:
                    written_data = json.load(f)
                    assert written_data == summary

class TestEvalRunnerIntegration:
    """Integration tests for evaluation runner."""
    
    @pytest.mark.asyncio
    async def test_run_no_traces(self):
        """Test running with no traces available."""
        mock_llm_client = AsyncMock()
        runner = EvalRunner(mock_llm_client)
        
        with patch.object(runner, 'load_existing_evaluations', return_value=set()), \
             patch.object(runner, 'load_traces', return_value=[]), \
             patch.object(runner, 'generate_metrics_summary', return_value={}), \
             patch.object(runner, 'write_summary') as mock_write:
            
            await runner.run()
            
            mock_write.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_dry_run(self):
        """Test dry run mode."""
        mock_llm_client = AsyncMock()
        runner = EvalRunner(mock_llm_client)
        
        mock_trace = RagTrace(
            trace_id="trace-001", timestamp="2025-11-19T10:00:00Z",
            intent="test", use_ai=True, routing_path="ai",
            retrieval_config={}, cypher_query=None, cypher_params={},
            neo4j_result_summary={}, prompt_system=None, prompt_user=None,
            llm_model_role=None, llm_model_id=None, final_answer=None
        )
        
        with patch.object(runner, 'load_existing_evaluations', return_value=set()), \
             patch.object(runner, 'load_traces', return_value=[mock_trace]), \
             patch.object(runner, 'filter_unevaluated_traces', return_value=[mock_trace]), \
             patch.object(runner, 'evaluate_batch') as mock_evaluate:
            
            await runner.run(dry_run=True)
            
            mock_evaluate.assert_not_called()

if __name__ == "__main__":
    pytest.main([__file__])