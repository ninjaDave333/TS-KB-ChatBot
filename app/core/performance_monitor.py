"""
Performance monitoring for TSKB-RAG system.
Tracks answer quality, response times, and system metrics.
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""
    timestamp: datetime
    query: str
    query_type: str
    execution_time: float
    confidence: float
    data_count: int
    success: bool
    error_message: Optional[str] = None

class PerformanceMonitor:
    """Monitor and track system performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.query_history: deque = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.query_type_stats = defaultdict(list)
        
    def record_query(self, 
                    query: str, 
                    query_type: str, 
                    execution_time: float, 
                    confidence: float, 
                    data_count: int, 
                    success: bool = True, 
                    error_message: Optional[str] = None):
        """Record metrics for a query execution."""
        
        metrics = QueryMetrics(
            timestamp=datetime.now(),
            query=query,
            query_type=query_type,
            execution_time=execution_time,
            confidence=confidence,
            data_count=data_count,
            success=success,
            error_message=error_message
        )
        
        self.query_history.append(metrics)
        
        if success:
            self.query_type_stats[query_type].append({
                'execution_time': execution_time,
                'confidence': confidence,
                'data_count': data_count
            })
        else:
            self.error_counts[error_message or 'Unknown error'] += 1
            
        logger.info(f"Query recorded: type={query_type}, time={execution_time:.2f}s, confidence={confidence}")
        
    def get_performance_summary(self, hours: int = 24) -> Dict:
        """Get performance summary for the last N hours."""
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_queries = [q for q in self.query_history if q.timestamp >= cutoff]
        
        if not recent_queries:
            return {"message": "No queries in the specified time period"}
            
        total_queries = len(recent_queries)
        successful_queries = [q for q in recent_queries if q.success]
        failed_queries = [q for q in recent_queries if not q.success]
        
        # Calculate averages for successful queries
        avg_execution_time = sum(q.execution_time for q in successful_queries) / len(successful_queries) if successful_queries else 0
        avg_confidence = sum(q.confidence for q in successful_queries) / len(successful_queries) if successful_queries else 0
        
        # Query type breakdown
        type_breakdown = defaultdict(int)
        for query in recent_queries:
            type_breakdown[query.query_type] += 1
            
        return {
            "time_period_hours": hours,
            "total_queries": total_queries,
            "successful_queries": len(successful_queries),
            "failed_queries": len(failed_queries),
            "success_rate": len(successful_queries) / total_queries * 100 if total_queries > 0 else 0,
            "average_execution_time": round(avg_execution_time, 2),
            "average_confidence": round(avg_confidence, 1),
            "query_type_breakdown": dict(type_breakdown),
            "top_errors": dict(list(self.error_counts.items())[:5]) if self.error_counts else {}
        }
        
    def get_query_type_performance(self, query_type: str) -> Dict:
        """Get detailed performance metrics for a specific query type."""
        
        if query_type not in self.query_type_stats:
            return {"error": f"No data for query type: {query_type}"}
            
        stats = self.query_type_stats[query_type]
        
        execution_times = [s['execution_time'] for s in stats]
        confidences = [s['confidence'] for s in stats]
        data_counts = [s['data_count'] for s in stats]
        
        return {
            "query_type": query_type,
            "total_queries": len(stats),
            "execution_time": {
                "average": round(sum(execution_times) / len(execution_times), 2),
                "min": round(min(execution_times), 2),
                "max": round(max(execution_times), 2)
            },
            "confidence": {
                "average": round(sum(confidences) / len(confidences), 1),
                "min": round(min(confidences), 1),
                "max": round(max(confidences), 1)
            },
            "data_count": {
                "average": round(sum(data_counts) / len(data_counts), 1),
                "min": min(data_counts),
                "max": max(data_counts)
            }
        }
        
    def get_health_status(self) -> Dict:
        """Get system health status based on recent performance."""
        
        recent_summary = self.get_performance_summary(hours=1)
        
        if recent_summary.get("total_queries", 0) == 0:
            return {"status": "idle", "message": "No recent queries"}
            
        success_rate = recent_summary.get("success_rate", 0)
        avg_confidence = recent_summary.get("average_confidence", 0)
        avg_time = recent_summary.get("average_execution_time", 0)
        
        # Health thresholds
        if success_rate >= 95 and avg_confidence >= 70 and avg_time <= 10:
            status = "healthy"
        elif success_rate >= 80 and avg_confidence >= 50 and avg_time <= 20:
            status = "warning"
        else:
            status = "critical"
            
        return {
            "status": status,
            "success_rate": success_rate,
            "average_confidence": avg_confidence,
            "average_execution_time": avg_time,
            "last_hour_queries": recent_summary.get("total_queries", 0)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()