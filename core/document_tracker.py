"""
Simple Document Tracker for GraphRAG System
Tracks which documents have been processed to avoid reprocessing
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

class DocumentTracker:
    """Tracks processed documents using file hashes"""
    
    def __init__(self, tracking_file: str = None):
        """Initialize the document tracker"""
        # Set default tracking file location
        if tracking_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tracking_file = os.path.join(base_dir, "core", "storage", "document_tracking.json")
        
        self.tracking_file = tracking_file
        self.processed_files = {}  # This is what was missing!
        self._ensure_tracking_directory()
        self._load_tracking_data()
    
    def _ensure_tracking_directory(self):
        """Ensure the tracking directory exists"""
        tracking_dir = os.path.dirname(self.tracking_file)
        os.makedirs(tracking_dir, exist_ok=True)
    
    def _load_tracking_data(self):
        """Load existing tracking data from file"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    self.processed_files = data.get('documents', {})
                print(f"📚 Loaded tracking data for {len(self.processed_files)} documents")
            except Exception as e:
                print(f"⚠️ Could not load tracking data: {e}")
                self.processed_files = {}
        else:
            print("📝 Starting with fresh document tracking")
            self.processed_files = {}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def is_processed(self, file_path: str) -> bool:
        """Check if a file has been processed"""
        file_path = str(file_path)
        
        # Check if file exists in tracking
        if file_path not in self.processed_files:
            return False
        
        # Check if file has changed since last processing
        current_hash = self._calculate_file_hash(file_path)
        stored_hash = self.processed_files[file_path].get('hash', '')
        
        if current_hash != stored_hash:
            print(f"📝 File has changed: {os.path.basename(file_path)}")
            return False
        
        return True
    
    def mark_processed(self, file_path: str, chunk_count: int = 0):
        """Mark a file as processed"""
        file_path = str(file_path)
        file_hash = self._calculate_file_hash(file_path)
        
        self.processed_files[file_path] = {
            'hash': file_hash,
            'processed_at': datetime.now().isoformat(),
            'chunks': chunk_count,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        print(f"✅ Marked as processed: {os.path.basename(file_path)}")
    
    def save(self):
        """Save tracking data to file"""
        try:
            data = {
                'documents': self.processed_files,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Saved tracking data for {len(self.processed_files)} documents")
        except Exception as e:
            print(f"❌ Error saving tracking data: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics about tracked documents"""
        total_docs = len(self.processed_files)
        total_chunks = sum(doc.get('chunks', 0) for doc in self.processed_files.values())
        
        return {
            'total_documents': total_docs,
            'total_chunks': total_chunks,
            'tracking_file': self.tracking_file
        }
    
    def clear(self):
        """Clear all tracking data"""
        self.processed_files = {}
        self.save()
        print("🧹 Cleared all tracking data")