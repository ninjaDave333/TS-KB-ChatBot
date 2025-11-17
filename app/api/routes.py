from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.neo4j_client import Neo4jClient
from app.core.query_generator import QueryGenerator
from app.core.bedrock_client import BedrockClient
from app.core.query_validator import CypherValidator
from app.core.answer_generator import AnswerGenerator
from app.core.performance_monitor import performance_monitor
import time

router = APIRouter()
neo4j_client = Neo4jClient()
query_generator = QueryGenerator()
bedrock_client = BedrockClient()
query_validator = CypherValidator()
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
    """Get system performance metrics."""
    return performance_monitor.get_performance_summary()

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

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    start_time = time.time()
    try:
        # Get schema for AI context
        schema = neo4j_client.get_schema()
        error_msg = None
        
        # Generate Cypher query
        if request.use_ai:
            try:
                print(f"Attempting AI generation for: {request.query}")
                cypher_query = bedrock_client.generate_cypher(request.query, schema)
                print(f"AI generated successfully: {cypher_query}")
                method = "ai_generated"
            except Exception as e:
                # Fallback to basic generator
                error_msg = f"AI failed: {str(e)}"
                print(f"Bedrock error: {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                cypher_query = query_generator.generate_cypher(request.query)
                method = "fallback_basic"
        else:
            cypher_query = query_generator.generate_cypher(request.query)
            method = "basic_rules"
        
        # Validate and fix query
        try:
            is_valid, fixed_query, validation_issues = query_validator.validate_and_fix(cypher_query)
            if not is_valid:
                print(f"Validation failed: {validation_issues}")
                error_msg = f"Query validation failed: {', '.join(validation_issues)}"
                # Don't use fallback for now, just use the fixed query anyway
                cypher_query = fixed_query
                method += "_validated"
            else:
                cypher_query = fixed_query
                if validation_issues:
                    print(f"Auto-fixed issues: {validation_issues}")
                    if error_msg:
                        error_msg += f"; Fixed: {', '.join(validation_issues)}"
                    else:
                        error_msg = f"Auto-fixed: {', '.join(validation_issues)}"
        except Exception as val_error:
            print(f"Validation error: {val_error}")
            # Continue with original query if validation fails
            pass
        
        # Execute query
        try:
            result = neo4j_client.execute_query(cypher_query)
        except Exception as e:
            # If execution still fails, try one more fallback
            if method != "validation_fallback":
                print(f"Query execution failed, trying fallback: {e}")
                cypher_query = query_generator.generate_cypher(request.query)
                method = "execution_fallback"
                result = neo4j_client.execute_query(cypher_query)
                if error_msg:
                    error_msg += f"; Execution fallback used"
                else:
                    error_msg = "Execution fallback used"
            else:
                raise e
        
        # Generate natural language answer
        answer = answer_generator.generate_answer(request.query, cypher_query, result)
        
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
        raise HTTPException(status_code=500, detail=str(e))