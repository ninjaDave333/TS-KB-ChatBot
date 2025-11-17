"""
Simple in-memory cache for TSKB-RAG system.
Caches query results and schema information.
"""

import time
import hashlib
import logging
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with data and metadata."""
    data: Any
    timestamp: float
    ttl: float
    hit_count: int = 0

class CacheManager:
    """Simple thread-safe in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
    def _generate_key(self, query: str, **kwargs) -> str:
        """Generate cache key from query and parameters."""
        key_data = f"{query}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get(self, query: str, **kwargs) -> Optional[Any]:
        """Get cached result for query."""
        key = self._generate_key(query, **kwargs)
        
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
                
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry.timestamp > entry.ttl:
                del self.cache[key]
                self.stats['evictions'] += 1
                self.stats['misses'] += 1
                return None
                
            # Update hit count and stats
            entry.hit_count += 1
            self.stats['hits'] += 1
            
            logger.debug(f"Cache hit for key: {key[:8]}...")
            return entry.data
            
    def set(self, query: str, data: Any, ttl: Optional[int] = None, **kwargs):
        """Cache result for query."""
        key = self._generate_key(query, **kwargs)
        ttl = ttl or self.default_ttl
        
        with self.lock:
            self.cache[key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl=ttl
            )
            
        logger.debug(f"Cached result for key: {key[:8]}... (TTL: {ttl}s)")
        
    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries. If pattern provided, only matching keys."""
        with self.lock:
            if pattern is None:
                # Clear all
                count = len(self.cache)
                self.cache.clear()
                logger.info(f"Cleared all cache entries: {count}")
            else:
                # Clear matching pattern
                keys_to_remove = [k for k in self.cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.cache[key]
                logger.info(f"Cleared {len(keys_to_remove)} cache entries matching: {pattern}")
                
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time - entry.timestamp > entry.ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.stats['evictions'] += 1
                
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'entries': len(self.cache),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'hit_rate': round(hit_rate, 1),
                'total_requests': total_requests
            }
            
    def get_cache_info(self) -> Dict:
        """Get detailed cache information."""
        with self.lock:
            entries_info = []
            current_time = time.time()
            
            for key, entry in list(self.cache.items())[:10]:  # Top 10 entries
                age = current_time - entry.timestamp
                remaining_ttl = max(0, entry.ttl - age)
                
                entries_info.append({
                    'key': key[:16] + '...',
                    'age_seconds': round(age, 1),
                    'remaining_ttl': round(remaining_ttl, 1),
                    'hit_count': entry.hit_count,
                    'data_size': len(str(entry.data))
                })
                
            return {
                'stats': self.get_stats(),
                'sample_entries': entries_info
            }

# Global cache instances
query_cache = CacheManager(default_ttl=300)  # 5 minutes for query results
schema_cache = CacheManager(default_ttl=3600)  # 1 hour for schema data