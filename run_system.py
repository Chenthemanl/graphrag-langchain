#!/usr/bin/env python3
"""
Easy startup script for GraphRAG Literature Review System
This script helps you get everything running with simple commands.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check for .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📝 Please create a .env file with:")
        print("GOOGLE_API_KEY=your_google_api_key")
        print("NEO4J_URI=bolt://localhost:7687")
        print("NEO4J_USERNAME=neo4j") 
        print("NEO4J_PASSWORD=your_password")
        return False
    
    # Check required directories
    files_dir = Path('core/files')
    storage_dir = Path('core/storage')
    
    if not files_dir.exists():
        print(f"📁 Creating files directory: {files_dir}")
        files_dir.mkdir(parents=True, exist_ok=True)
    
    if not storage_dir.exists():
        print(f"📁 Creating storage directory: {storage_dir}")
        storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for documents
    doc_files = list(files_dir.glob('*.pdf')) + list(files_dir.glob('*.docx')) + list(files_dir.glob('*.txt'))
    
    print(f"📄 Found {len(doc_files)} documents in {files_dir}")
    if doc_files:
        for doc in doc_files[:5]:  # Show first 5 files
            print(f"   - {doc.name}")
        if len(doc_files) > 5:
            print(f"   ... and {len(doc_files) - 5} more")
    else:
        print("⚠️  No documents found. Add PDF, DOCX, or TXT files to core/files/")
    
    return True

def show_embeddings_info():
    """Show information about stored embeddings"""
    try:
        from core.embedding_cache import EmbeddingCache
        cache = EmbeddingCache()
        stats = cache.get_stats()
        
        print("\n📊 Embeddings Information:")
        print(f"   Total embeddings: {stats.get('total_embeddings', 0)}")
        print(f"   Cache file: {stats.get('cache_file', 'Not found')}")
        print(f"   Cache size: {stats.get('cache_size_mb', 0):.2f} MB")
        
        # Show cache file location
        cache_file = Path(stats.get('cache_file', ''))
        if cache_file.exists():
            print(f"   📍 You can view embeddings at: {cache_file.absolute()}")
        
    except Exception as e:
        print(f"⚠️  Could not load embeddings info: {e}")

def run_backend_only():
    """Run just the backend processing"""
    print("🚀 Running backend processing...")
    try:
        # Run as module to fix import issues
        subprocess.run([sys.executable, "-m", "core.main_with_llmgraphtranformer"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend processing failed: {e}")
        # Try alternative method
        try:
            print("🔄 Trying alternative method...")
            os.chdir("core")
            subprocess.run([sys.executable, "main_with_llmgraphtranformer.py"], check=True)
            os.chdir("..")
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False
    return True

def run_web_interface():
    """Run the full web interface"""
    print("🌐 Starting web interface...")
    print("📍 Will be available at: http://localhost:5001")
    try:
        subprocess.run([sys.executable, "api_bridge.py"])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Web interface failed: {e}")

def run_fastapi():
    """Run the FastAPI version"""
    print("🚀 Starting FastAPI server...")
    print("📍 Will be available at: http://localhost:8000")
    print("📍 API docs at: http://localhost:8000/docs")
    try:
        subprocess.run([sys.executable, "start_api.py"])
    except KeyboardInterrupt:
        print("\n👋 FastAPI server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI failed: {e}")

def process_documents():
    """Process documents with various options"""
    print("📄 Document Processing Options:")
    print("1. Process new/changed documents only")
    print("2. Force reprocess all documents")  
    print("3. Clean database and reprocess all")
    print("4. Test system only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    args = []
    if choice == "2":
        args.append("--force-reprocess")
    elif choice == "3":
        args.extend(["--force-reprocess", "--clean-neo4j"])
    elif choice == "4":
        args.append("--test-only")
    
    try:
        # Try running as module first
        cmd = [sys.executable, "-m", "core.main_with_llmgraphtranformer"] + args
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Module method failed: {e}")
        # Try alternative method
        try:
            print("🔄 Trying alternative method...")
            original_dir = os.getcwd()
            os.chdir("core")
            cmd = [sys.executable, "main_with_llmgraphtranformer.py"] + args
            subprocess.run(cmd, check=True)
            os.chdir(original_dir)
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            print("\n🔧 Manual fix needed - see instructions below")

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Literature Review System")
    parser.add_argument("--web", action="store_true", help="Start web interface (recommended)")
    parser.add_argument("--api", action="store_true", help="Start FastAPI server")
    parser.add_argument("--backend", action="store_true", help="Run backend processing only")
    parser.add_argument("--process", action="store_true", help="Process documents interactively")
    parser.add_argument("--embeddings", action="store_true", help="Show embeddings information")
    parser.add_argument("--check", action="store_true", help="Check environment setup")
    
    args = parser.parse_args()
    
    print("🎯 GraphRAG Literature Review System")
    print("=" * 50)
    
    # Always check environment first
    if not check_environment():
        return
    
    if args.embeddings:
        show_embeddings_info()
        return
    
    if args.check:
        print("✅ Environment check complete!")
        return
    
    if args.process:
        process_documents()
        return
    
    if args.backend:
        run_backend_only()
        return
    
    if args.api:
        run_fastapi()
        return
    
    if args.web:
        run_web_interface()
        return
    
    # No arguments provided - show interactive menu
    print("\n🚀 What would you like to do?")
    print("1. Start web interface (recommended)")
    print("2. Start FastAPI server")
    print("3. Process documents only")
    print("4. View embeddings info")
    print("5. Check environment setup")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        run_web_interface()
    elif choice == "2":
        run_fastapi()
    elif choice == "3":
        process_documents()
    elif choice == "4":
        show_embeddings_info()
    elif choice == "5":
        check_environment()
        print("✅ Environment check complete!")
    else:
        print("❌ Invalid choice. Please run with --help for options.")

if __name__ == "__main__":
    main()