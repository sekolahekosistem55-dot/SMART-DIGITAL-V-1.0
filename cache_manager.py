import hashlib
import json
from typing import Optional, Dict, Any
from database import DatabaseManager
from config import Config

class CacheManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate MD5 hash for caching"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_cached_response(self, query: str, subject: str, grade_level: str) -> Optional[str]:
        """Get cached response if exists"""
        query_hash = self._generate_hash({
            "query": query,
            "subject": subject,
            "grade_level": grade_level
        })
        return self.db.get_cache(query_hash)
    
    def save_to_cache(self, query: str, response: str, subject: str, grade_level: str):
        """Save response to cache"""
        query_hash = self._generate_hash({
            "query": query,
            "subject": subject,
            "grade_level": grade_level
        })
        self.db.set_cache(query_hash, query, response, subject, grade_level)
    
    def clear_old_cache(self):
        """Clear expired cache entries"""
        # This can be run as a background job
        pass
