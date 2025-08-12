# api_bridge.py
"""
API bridge to connect your frontend to GraphRAG system
Place this file in your graphrag-langchain folder
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import tempfile

# Import your GraphRAG system (adjust based on your actual file names)
try:
    # Import from your main GraphRAG file
    from core.main_with_llmgraphtranformer import main as graphrag_main
    from core.document_tracker import DocumentTracker
    from core.config import FILES_DIRECTORY
    print("✅ Successfully imported GraphRAG system")
except ImportError as e:
    print(f"❌ Could not import GraphRAG system: {e}")
    print("Make sure you're running this from the graphrag-langchain directory")

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Global variables to store our GraphRAG system
chain = None
vector_store = None
graph = None
tracker = None

# Path to your frontend files (in the article-analyzer folder)
FRONTEND_PATH = "."  # Frontend files are in the same directory now

def initialize_graphrag():
    """Initialize the GraphRAG system"""
    global chain, vector_store, graph, tracker
    try:
        print("🚀 Initializing GraphRAG system...")
        chain, vector_store, graph = graphrag_main(
            force_reprocess=False,
            clean_neo4j=False,
            use_chromadb=False  # Start with in-memory
        )
        tracker = DocumentTracker()
        print("✅ GraphRAG system initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize GraphRAG: {e}")
        return False

@app.route('/')
def serve_frontend():
    """Serve the main HTML file from article-analyzer folder"""
    return send_from_directory(FRONTEND_PATH, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.) from article-analyzer folder"""
    try:
        return send_from_directory(FRONTEND_PATH, filename)
    except:
        return f"File not found: {filename}", 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Check if the GraphRAG system is ready"""
    global chain
    if chain is None:
        return jsonify({
            "status": "not_initialized",
            "message": "GraphRAG system not initialized"
        }), 500
    
    return jsonify({
        "status": "ready",
        "message": "GraphRAG system is ready",
        "documents_processed": len(tracker.processed_files) if tracker else 0
    })

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize or reinitialize the GraphRAG system"""
    force_reprocess = request.json.get('force_reprocess', False) if request.is_json else False
    
    try:
        global chain, vector_store, graph
        chain, vector_store, graph = graphrag_main(
            force_reprocess=force_reprocess,
            clean_neo4j=False,
            use_chromadb=False
        )
        return jsonify({
            "status": "success",
            "message": "GraphRAG system initialized successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize: {str(e)}"
        }), 500

@app.route('/api/add_document', methods=['POST'])
def add_document():
    """Add a new document to the GraphRAG system"""
    global chain, vector_store, graph, tracker
    
    try:
        # Get the text content and filename from the request
        data = request.json
        text_content = data.get('content', '').strip()
        filename = data.get('filename', f'document_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        
        if not text_content:
            return jsonify({
                "status": "error",
                "message": "No content provided"
            }), 400
        
        # Ensure the files directory exists
        os.makedirs(FILES_DIRECTORY, exist_ok=True)
        
        # Save the content to a file
        file_path = os.path.join(FILES_DIRECTORY, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Reinitialize the system to process the new document
        chain, vector_store, graph = graphrag_main(
            force_reprocess=False,  # Only process new documents
            clean_neo4j=False,
            use_chromadb=False
        )
        
        return jsonify({
            "status": "success",
            "message": f"Document '{filename}' added successfully",
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to add document: {str(e)}"
        }), 500

@app.route('/api/query', methods=['POST'])
def query_graphrag():
    """Query the GraphRAG system"""
    global chain
    
    if chain is None:
        return jsonify({
            "status": "error",
            "message": "GraphRAG system not initialized. Please add documents first."
        }), 400
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                "status": "error",
                "message": "No question provided"
            }), 400
        
        # Query the GraphRAG system
        answer = chain.invoke(question)
        
        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Query failed: {str(e)}"
        }), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all processed documents"""
    global tracker
    
    if tracker is None:
        return jsonify({
            "status": "error",
            "message": "System not initialized"
        }), 400
    
    try:
        documents = []
        for file_path, info in tracker.processed_files.items():
            documents.append({
                "filename": os.path.basename(file_path),
                "path": file_path,
                "chunks": info.get('chunks', 0),
                "processed_at": info.get('processed_at', 'Unknown')
            })
        
        return jsonify({
            "status": "success",
            "documents": documents,
            "total": len(documents)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to list documents: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🌟 Starting GraphRAG API Bridge...")
    print("📁 GraphRAG files: ./")
    print(f"📁 Frontend files: {FRONTEND_PATH}")
    print("🔗 Application will be available at: http://localhost:5000")
    
    # Try to initialize the GraphRAG system
    if initialize_graphrag():
        print("🎉 Ready to go! Open http://localhost:5000 in your browser")
    else:
        print("⚠️  GraphRAG system not initialized, but server will start anyway")
        print("💡 Try adding some documents first!")
    
app.run(debug=True, host='0.0.0.0', port=5001)
