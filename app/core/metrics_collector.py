"""
Production metrics collector for monitoring RAG performance.
Tracks: query performance, intent distribution, validation stats, errors.
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from collections import defaultdict
import threading

class MetricsCollector:
    """Thread-safe metrics collector for production monitoring."""
    
    def __init__(self, metrics_file: str = "data/production_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
        # In-memory metrics
        self.total_queries = 0
        self.intent_counts = defaultdict(int)
        self.validation_attempts = defaultdict(int)  # {1: count, 2: count}
        self.errors = defaultdict(int)
        self.response_times = []
        self.query_history = []  # Last 100 queries
        
        # Load existing metrics
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from disk if exists."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.total_queries = data.get('total_queries', 0)
                    self.intent_counts = defaultdict(int, data.get('intent_counts', {}))
                    self.validation_attempts = defaultdict(int, data.get('validation_attempts', {}))
                    self.errors = defaultdict(int, data.get('errors', {}))
                    self.response_times = data.get('response_times', [])[-1000:]  # Keep last 1000
                    self.query_history = data.get('query_history', [])[-100:]  # Keep last 100
            except Exception as e:
                print(f"Failed to load metrics: {e}")
    
    def _save_metrics(self):
        """Persist metrics to disk."""
        try:
            data = {
                'total_queries': self.total_queries,
                'intent_counts': dict(self.intent_counts),
                'validation_attempts': dict(self.validation_attempts),
                'errors': dict(self.errors),
                'response_times': self.response_times[-1000:],
                'query_history': self.query_history[-100:],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save metrics: {e}")
    
    def record_query(self, 
                     query: str,
                     intent: str,
                     validation_attempts: int,
                     response_time: float,
                     success: bool,
                     error: Optional[str] = None):
        """Record a query execution."""
        with self._lock:
            self.total_queries += 1
            self.intent_counts[intent] += 1
            self.validation_attempts[validation_attempts] += 1
            self.response_times.append(response_time)
            
            if not success and error:
                self.errors[error] += 1
            
            # Add to history
            self.query_history.append({
                'timestamp': datetime.now().isoformat(),
                'query': query[:100],  # Truncate long queries
                'intent': intent,
                'validation_attempts': validation_attempts,
                'response_time': round(response_time, 2),
                'success': success,
                'error': error
            })
            
            # Keep only last 100
            if len(self.query_history) > 100:
                self.query_history = self.query_history[-100:]
            
            # Persist every 10 queries
            if self.total_queries % 10 == 0:
                self._save_metrics()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            return {
                'total_queries': self.total_queries,
                'intent_distribution': dict(self.intent_counts),
                'validation_attempts': dict(self.validation_attempts),
                'errors': dict(self.errors),
                'performance': {
                    'avg_response_time': round(avg_response_time, 2),
                    'min_response_time': round(min(self.response_times), 2) if self.response_times else 0,
                    'max_response_time': round(max(self.response_times), 2) if self.response_times else 0,
                },
                'recent_queries': self.query_history[-20:],  # Last 20
                'last_updated': datetime.now().isoformat()
            }
    
    def reset_metrics(self):
        """Reset all metrics (for testing)."""
        with self._lock:
            self.total_queries = 0
            self.intent_counts.clear()
            self.validation_attempts.clear()
            self.errors.clear()
            self.response_times.clear()
            self.query_history.clear()
            self._save_metrics()

# Global instance
metrics_collector = MetricsCollector()
