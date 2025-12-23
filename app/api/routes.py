from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..auth.jwt_dependencies import get_jwt_user
from app.database.neo4j_client import Neo4jClient
from app.core.query_generator import QueryGenerator
from app.core.enhanced_query_generator import EnhancedQueryGenerator
from app.core.production_learning_loader import ProductionLearningLoader
from app.core.bedrock_client import BedrockClient
from app.core.llm_client import LLMClient
from app.core.answer_generator import AnswerGenerator
from app.core.answer_renderer import render_answer
from app.core.performance_monitor import performance_monitor
from app.core.metrics_collector import metrics_collector
from app.core.config import get_rag_config
from app.core.tracing import new_trace, safe_write_trace
import time

router = APIRouter()
neo4j_client = Neo4jClient()
query_generator = QueryGenerator()
enhanced_generator = EnhancedQueryGenerator()

# Load production learning patterns
ProductionLearningLoader.load_production_patterns(enhanced_generator)

# Initialize LLMClient and BedrockClient
llm_client = LLMClient()
bedrock_client = BedrockClient(llm_client)
answer_generator = AnswerGenerator()

class QueryRequest(BaseModel):
    query: str
    use_ai: bool = True

class QueryResponse(BaseModel):
    query: str
    answer: str
    data: list
    cypher_query: str
    method: str
    execution_time: float
    error: Optional[str] = None

@router.get("/health")
async def health_check():
    try:
        # Test Neo4j connection
        result = neo4j_client.execute_query("RETURN 1 as test")
        return {"status": "healthy", "neo4j": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/schema")
async def get_schema():
    try:
        schema = neo4j_client.get_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """Get production monitoring metrics."""
    return metrics_collector.get_metrics()

@router.get("/health/detailed")
async def detailed_health():
    """Get detailed health status including performance metrics."""
    try:
        # Test Neo4j connection
        neo4j_result = neo4j_client.execute_query("RETURN 1 as test")
        neo4j_status = "connected"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"
    
    health_status = performance_monitor.get_health_status()
    
    return {
        "status": health_status["status"],
        "neo4j": neo4j_status,
        "performance": health_status,
        "metrics_summary": performance_monitor.get_performance_summary(hours=1)
    }

@router.get("/learning/insights")
async def get_learning_insights():
    """Get insights about the learning process."""
    try:
        insights = enhanced_generator.get_learning_insights()
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/patterns")
async def get_pattern_suggestions():
    """Get suggestions for new query patterns."""
    try:
        suggestions = enhanced_generator.get_pattern_suggestions()
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/trends")
async def analyze_query_trends(hours: int = 24):
    """Analyze recent query trends."""
    try:
        trends = enhanced_generator.analyze_query_trends(hours)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/export")
async def export_learning_data():
    """Export learning data for analysis or backup."""
    try:
        data = enhanced_generator.export_learning_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning/suggest")
async def suggest_query_improvements(request: QueryRequest):
    """Get suggestions for query improvements based on production patterns."""
    try:
        suggestions = enhanced_generator.optimizer.suggest_query_improvements(request.query)
        return {"query": request.query, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FeedbackRequest(BaseModel):
    query: str
    cypher: str
    execution_time: float
    data_count: int
    user_rating: Optional[float] = None

@router.post("/learning/feedback")
async def record_feedback(request: FeedbackRequest):
    """Record feedback for query learning."""
    try:
        enhanced_generator.record_query_success(
            query=request.query,
            cypher=request.cypher,
            execution_time=request.execution_time,
            data_count=request.data_count,
            user_feedback=request.user_rating
        )
        return {"status": "feedback_recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, user: dict = Depends(get_jwt_user)):
    start_time = time.time()
    
    # Initialize tracing
    trace = new_trace(intent=None, use_ai=request.use_ai, routing_path=None)
    
    try:
        # Get schema for AI context
        schema = neo4j_client.get_schema()
        error_msg = None
        
        # Generate Cypher query with dynamic learning
        intent = None
        validation_attempts = 1
        if request.use_ai:
            try:
                print(f"Attempting AI generation for: {request.query}")
                # ALWAYS use AI generation (like CLI demo) - validation handled in BedrockClient
                cypher_query, intent, validation_attempts = await bedrock_client.generate_cypher(request.query, schema, trace)
                print(f"AI generated successfully: {cypher_query}")
                method = "ai_generated"
            except Exception as e:
                # Fallback to enhanced generator traditional method
                error_msg = f"AI failed: {str(e)}"
                print(f"Bedrock error: {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                enhanced_result = enhanced_generator.generate_cypher_with_learning(request.query)
                cypher_query = enhanced_result['cypher']
                method = f"enhanced_fallback ({enhanced_result['method']})"
        else:
            # Use enhanced generator for better pattern recognition
            enhanced_result = enhanced_generator.generate_cypher_with_learning(request.query)
            cypher_query = enhanced_result['cypher']
            method = f"enhanced_basic ({enhanced_result['method']})"
        
        # Execute query (validation already done in BedrockClient)
        # Record Cypher in trace
        trace.cypher_query = cypher_query
        trace.cypher_params = {}  # No params in current implementation
        
        try:
            result = neo4j_client.execute_query(cypher_query)
            
            # Record Neo4j result summary in trace
            trace.neo4j_result_summary = {
                "record_count": len(result),
                "has_data": len(result) > 0
            }
        except Exception as e:
            # Log the error and re-raise - don't hide execution failures
            print(f"Query execution failed: {e}")
            print(f"Failed Cypher: {cypher_query}")
            raise
        
        # Generate natural language answer using LLM
        try:
            answer = await render_answer(request.query, result, bedrock_client)
        except Exception as e:
            print(f"Answer rendering failed, using fallback: {e}")
            # Fallback to rule-based generator
            answer = answer_generator.generate_answer(request.query, cypher_query, result)
        
        # Record routing path in trace
        trace.routing_path = method
        trace.intent = answer_generator._detect_query_type(request.query)
        
        # Record performance metrics
        execution_time = time.time() - start_time
        query_type = answer_generator._detect_query_type(request.query)
        confidence = 85 if method.startswith("ai_") else 70
        
        performance_monitor.record_query(
            query=request.query,
            query_type=query_type,
            execution_time=execution_time,
            confidence=confidence,
            data_count=len(result),
            success=True
        )
        
        # Record successful query for learning (if data was returned)
        if len(result) > 0:
            enhanced_generator.record_query_success(
                query=request.query,
                cypher=cypher_query,
                execution_time=execution_time,
                data_count=len(result)
            )
        
        # Record metrics
        metrics_collector.record_query(
            query=request.query,
            intent=intent or "unknown",
            validation_attempts=validation_attempts,
            response_time=execution_time,
            success=True
        )
        
        # Complete trace before returning
        trace.final_answer = answer
        safe_write_trace(trace)
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            data=result,
            cypher_query=cypher_query,
            method=method,
            execution_time=execution_time,
            error=error_msg
        )
    
    except Exception as e:
        # Record metrics for failure
        execution_time = time.time() - start_time
        metrics_collector.record_query(
            query=request.query,
            intent="unknown",
            validation_attempts=1,
            response_time=execution_time,
            success=False,
            error=type(e).__name__
        )
        
        # Record query failure for learning
        try:
            enhanced_generator.record_query_failure(
                query=request.query,
                error_type=type(e).__name__,
                error_details=str(e)
            )
        except:
            pass  # Don't let learning failure affect main error handling
        
        raise HTTPException(status_code=500, detail=str(e))