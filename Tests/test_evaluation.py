"""
Unit tests for judge model evaluation functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
from app.core.evaluation import EvalResult, write_eval, safe_write_eval
from app.core.judge_client import judge_answer, evaluate_trace
from app.core.tracing import new_trace

class TestEvalResult:
    """Test EvalResult dataclass functionality."""
    
    def test_eval_result_creation(self):
        """Test that EvalResult can be created with all fields."""
        eval_result = EvalResult(
            trace_id="test-trace-123",
            overall_score=8.5,
            factual_correctness=9.0,
            grounded_in_context=8.0,
            helpfulness=8.5,
            error_type="none",
            raw_judge_response='{"overall_score": 8.5}'
        )
        
        assert eval_result.trace_id == "test-trace-123"
        assert eval_result.overall_score == 8.5
        assert eval_result.factual_correctness == 9.0
        assert eval_result.grounded_in_context == 8.0
        assert eval_result.helpfulness == 8.5
        assert eval_result.error_type == "none"
        assert eval_result.raw_judge_response == '{"overall_score": 8.5}'

class TestEvalWriting:
    """Test evaluation result writing functionality."""
    
    def test_write_eval_creates_valid_jsonl(self):
        """Test that write_eval creates valid JSONL format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_eval.jsonl"
            
            with patch('app.core.evaluation.EVAL_FILE', test_file):
                eval_result = EvalResult(
                    trace_id="test-123",
                    overall_score=7.5,
                    factual_correctness=8.0,
                    grounded_in_context=7.0,
                    helpfulness=8.0,
                    error_type="none"
                )
                
                write_eval(eval_result)
                
                # Verify file was created and contains valid JSON
                assert test_file.exists()
                
                with test_file.open("r") as f:
                    line = f.readline().strip()
                    data = json.loads(line)
                    
                    assert data["trace_id"] == "test-123"
                    assert data["overall_score"] == 7.5
                    assert data["factual_correctness"] == 8.0
                    assert data["error_type"] == "none"
    
    def test_safe_write_eval_handles_errors(self):
        """Test that safe_write_eval doesn't raise exceptions."""
        with patch('app.core.evaluation.write_eval', side_effect=Exception("Test error")):
            eval_result = EvalResult(
                trace_id="test",
                overall_score=5.0,
                factual_correctness=5.0,
                grounded_in_context=5.0,
                helpfulness=5.0,
                error_type="none"
            )
            
            # Should not raise exception
            safe_write_eval(eval_result)

class TestJudgeAnswer:
    """Test judge model answer evaluation."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLMClient for testing."""
        mock_client = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def valid_judge_response(self):
        """Sample valid judge model response."""
        return json.dumps({
            "overall_score": 8.5,
            "factual_correctness": 9.0,
            "grounded_in_context": 8.0,
            "helpfulness": 8.5,
            "error_type": "none"
        })
    
    @pytest.mark.asyncio
    async def test_judge_answer_success(self, mock_llm_client, valid_judge_response):
        """Test successful judge model evaluation."""
        mock_llm_client.complete.return_value = valid_judge_response
        
        result = await judge_answer(
            llm_client=mock_llm_client,
            question="How many clients are there?",
            answer="There are 150 clients in the system.",
            context="Cypher: MATCH (c:Client) RETURN count(c)"
        )
        
        assert result["status"] == "success"
        assert result["evaluation"]["overall_score"] == 8.5
        assert result["evaluation"]["factual_correctness"] == 9.0
        assert result["evaluation"]["error_type"] == "none"
        assert result["raw_response"] == valid_judge_response
        
        # Verify LLM was called with judge role
        mock_llm_client.complete.assert_called_once()
        call_args = mock_llm_client.complete.call_args
        assert call_args[1]["role"] == "judge"
    
    @pytest.mark.asyncio
    async def test_judge_answer_invalid_json(self, mock_llm_client):
        """Test judge model returning invalid JSON."""
        mock_llm_client.complete.return_value = "Invalid JSON response"
        
        result = await judge_answer(
            llm_client=mock_llm_client,
            question="Test question",
            answer="Test answer",
            context="Test context"
        )
        
        assert result["status"] == "json_error"
        assert "error" in result
        assert result["raw_response"] == "Invalid JSON response"
    
    @pytest.mark.asyncio
    async def test_judge_answer_llm_error(self, mock_llm_client):
        """Test judge model LLM call failure."""
        mock_llm_client.complete.side_effect = Exception("LLM API error")
        
        result = await judge_answer(
            llm_client=mock_llm_client,
            question="Test question",
            answer="Test answer",
            context="Test context"
        )
        
        assert result["status"] == "error"
        assert "LLM API error" in result["error"]

class TestEvaluateTrace:
    """Test trace evaluation functionality."""
    
    @pytest.fixture
    def sample_trace(self):
        """Create a sample trace for testing."""
        trace = new_trace("count_query", True, "ai_generated")
        trace.prompt_user = "How many clients are there?"
        trace.cypher_query = "MATCH (c:Client) RETURN count(c) as clientCount"
        trace.neo4j_result_summary = {"record_count": 1, "has_data": True}
        trace.final_answer = "There are 150 clients in the system."
        return trace
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLMClient for testing."""
        mock_client = AsyncMock()
        return mock_client
    
    @pytest.mark.asyncio
    async def test_evaluate_trace_success(self, mock_llm_client, sample_trace):
        """Test successful trace evaluation."""
        judge_response = json.dumps({
            "overall_score": 8.5,
            "factual_correctness": 9.0,
            "grounded_in_context": 8.0,
            "helpfulness": 8.5,
            "error_type": "none"
        })
        mock_llm_client.complete.return_value = judge_response
        
        eval_result = await evaluate_trace(mock_llm_client, sample_trace)
        
        assert eval_result is not None
        assert eval_result.trace_id == sample_trace.trace_id
        assert eval_result.overall_score == 8.5
        assert eval_result.factual_correctness == 9.0
        assert eval_result.grounded_in_context == 8.0
        assert eval_result.helpfulness == 8.5
        assert eval_result.error_type == "none"
        assert eval_result.raw_judge_response == judge_response
    
    @pytest.mark.asyncio
    async def test_evaluate_trace_judge_failure(self, mock_llm_client, sample_trace):
        """Test trace evaluation when judge model fails."""
        mock_llm_client.complete.side_effect = Exception("Judge model error")
        
        eval_result = await evaluate_trace(mock_llm_client, sample_trace)
        
        assert eval_result is None
    
    @pytest.mark.asyncio
    async def test_evaluate_trace_builds_context(self, mock_llm_client, sample_trace):
        """Test that evaluate_trace builds context from trace data."""
        judge_response = json.dumps({
            "overall_score": 7.0,
            "factual_correctness": 7.0,
            "grounded_in_context": 7.0,
            "helpfulness": 7.0,
            "error_type": "none"
        })
        mock_llm_client.complete.return_value = judge_response
        
        await evaluate_trace(mock_llm_client, sample_trace)
        
        # Verify judge_answer was called with context built from trace
        mock_llm_client.complete.assert_called_once()
        call_args = mock_llm_client.complete.call_args
        user_prompt = call_args[0][1]  # Second argument is user_prompt
        
        assert "How many clients are there?" in user_prompt
        assert "There are 150 clients in the system." in user_prompt
        assert "MATCH (c:Client) RETURN count(c)" in user_prompt

class TestEvaluationIntegration:
    """Test evaluation integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_evaluation_lifecycle(self):
        """Test complete evaluation from trace to written result."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "integration_eval.jsonl"
            
            with patch('app.core.evaluation.EVAL_FILE', test_file):
                # Create trace
                trace = new_trace("count_query", True, "ai_generated")
                trace.prompt_user = "How many clients are there?"
                trace.final_answer = "There are 150 clients."
                trace.cypher_query = "MATCH (c:Client) RETURN count(c)"
                trace.neo4j_result_summary = {"record_count": 1}
                
                # Mock LLM client
                mock_llm_client = AsyncMock()
                judge_response = json.dumps({
                    "overall_score": 8.0,
                    "factual_correctness": 8.5,
                    "grounded_in_context": 7.5,
                    "helpfulness": 8.0,
                    "error_type": "none"
                })
                mock_llm_client.complete.return_value = judge_response
                
                # Evaluate trace
                eval_result = await evaluate_trace(mock_llm_client, trace)
                
                # Write evaluation
                write_eval(eval_result)
                
                # Verify evaluation was written correctly
                with test_file.open("r") as f:
                    data = json.loads(f.readline())
                    
                    assert data["trace_id"] == trace.trace_id
                    assert data["overall_score"] == 8.0
                    assert data["factual_correctness"] == 8.5
                    assert data["grounded_in_context"] == 7.5
                    assert data["helpfulness"] == 8.0
                    assert data["error_type"] == "none"
                    assert data["raw_judge_response"] == judge_response

if __name__ == "__main__":
    pytest.main([__file__])