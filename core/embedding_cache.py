"""
Simple Embedding Cache for GraphRAG System
Caches embeddings to avoid regenerating them
"""

import json
import os
import hashlib
from typing import List, Optional, Dict

class EmbeddingCache:
    """Cache for document embeddings to avoid regeneration"""
    
    def __init__(self, cache_file: str = None):
        """Initialize the embedding cache"""
        # Set default cache file location
        if cache_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_file = os.path.join(base_dir, "core", "storage", "embedding_cache.json")
        
        self.cache_file = cache_file
        self._cache = {}  # Internal cache storage
        self._ensure_cache_directory()
        self._load_cache()
    
    def _ensure_cache_directory(self):
        """Ensure the cache directory exists"""
        cache_dir = os.path.dirname(self.cache_file)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _load_cache(self):
        """Load existing cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self._cache = json.load(f)
                print(f"📦 Loaded {len(self._cache)} cached embeddings")
            except Exception as e:
                print(f"⚠️ Could not load embedding cache: {e}")
                self._cache = {}
        else:
            print("🆕 Starting with fresh embedding cache")
            self._cache = {}
    
    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for text"""
        # Use SHA256 hash of text as cache key
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text if it exists"""
        cache_key = self._get_cache_key(text)
        return self._cache.get(cache_key)
    
    def add_embedding(self, text: str, embedding: List[float]):
        """Add an embedding to the cache"""
        cache_key = self._get_cache_key(text)
        self._cache[cache_key] = embedding
    
    def save(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f)
            print(f"💾 Saved {len(self._cache)} embeddings to cache")
        except Exception as e:
            print(f"❌ Error saving embedding cache: {e}")
    
    def clear(self):
        """Clear the cache"""
        self._cache = {}
        self.save()
        print("🧹 Cleared embedding cache")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_embeddings': len(self._cache),
            'cache_file': self.cache_file,
            'cache_size_mb': len(json.dumps(self._cache)) / (1024 * 1024)
        }