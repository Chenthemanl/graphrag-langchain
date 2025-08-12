# api_bridge.py
"""
API bridge to connect your frontend to GraphRAG system
Fixed version with correct MIME types for module scripts
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
import tempfile
import mimetypes

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
    graphrag_main = None
    DocumentTracker = None
    FILES_DIRECTORY = "core/files"

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Set up proper MIME types
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('application/typescript', '.ts')
mimetypes.add_type('text/typescript', '.tsx')
mimetypes.add_type('text/css', '.css')

# Global variables to store our GraphRAG system
chain = None
vector_store = None
graph = None
tracker = None

# Path to your frontend files (in the same directory now)
FRONTEND_PATH = "."  # Frontend files are in the same directory now

def initialize_graphrag():
    """Initialize the GraphRAG system"""
    global chain, vector_store, graph, tracker
    
    if graphrag_main is None:
        print("❌ GraphRAG main function not available")
        return False
        
    try:
        print("🚀 Initializing GraphRAG system...")
        chain, vector_store, graph = graphrag_main(
            force_reprocess=False,
            clean_neo4j=False,
            use_chromadb=False  # Start with in-memory
        )
        
        if DocumentTracker:
            tracker = DocumentTracker()
        else:
            tracker = None
            
        print("✅ GraphRAG system initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize GraphRAG: {e}")
        return False

@app.route('/')
def serve_frontend():
    """Serve the main HTML file"""
    return send_from_directory(FRONTEND_PATH, 'index.html')

@app.route('/index.css')
def serve_css():
    """Serve CSS with correct MIME type"""
    return send_from_directory(FRONTEND_PATH, 'index.css', mimetype='text/css')

@app.route('/index.js')
def serve_js():
    """Serve JavaScript file with correct MIME type"""
    return send_from_directory(FRONTEND_PATH, 'index.js', mimetype='application/javascript')

@app.route('/index.tsx')
def serve_tsx():
    """Serve TypeScript/JSX files as JavaScript modules"""
    try:
        # Try to serve index.js if it exists, otherwise fallback to index.tsx
        js_path = os.path.join(FRONTEND_PATH, 'index.js')
        if os.path.exists(js_path):
            return send_from_directory(FRONTEND_PATH, 'index.js', mimetype='application/javascript')
        
        # Fallback to index.tsx if index.js doesn't exist
        file_path = os.path.join(FRONTEND_PATH, 'index.tsx')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Return with correct MIME type for ES modules
        return Response(content, mimetype='application/javascript')
    except Exception as e:
        return f"Error loading JavaScript: {e}", 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files with correct MIME types"""
    try:
        # Determine correct MIME type based on file extension
        if filename.endswith('.js') or filename.endswith('.mjs'):
            mimetype = 'application/javascript'
        elif filename.endswith('.tsx') or filename.endswith('.ts'):
            # Serve TypeScript files as JavaScript for browser
            mimetype = 'application/javascript'
        elif filename.endswith('.css'):
            mimetype = 'text/css'
        elif filename.endswith('.html'):
            mimetype = 'text/html'
        else:
            mimetype = None
            
        return send_from_directory(FRONTEND_PATH, filename, mimetype=mimetype)
    except:
        return f"File not found: {filename}", 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Check if the GraphRAG system is ready"""
    global chain, tracker
    
    # Try to initialize if not already done
    if chain is None:
        initialize_graphrag()
    
    if chain is None:
        return jsonify({
            "status": "not_initialized",
            "message": "GraphRAG system not initialized - add documents to start"
        }), 200  # Return 200 instead of 500 to avoid error
    
    doc_count = 0
    if tracker and hasattr(tracker, 'processed_files'):
        doc_count = len(tracker.processed_files)
    
    return jsonify({
        "status": "ready",
        "message": "GraphRAG system is ready",
        "documents_processed": doc_count
    })

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize or reinitialize the GraphRAG system"""
    if graphrag_main is None:
        return jsonify({
            "status": "error",
            "message": "GraphRAG system not available"
        }), 500
        
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
    """Add a new document to the GraphRAG system - supports text, PDF, and DOCX"""
    global chain, vector_store, graph, tracker
    
    if graphrag_main is None:
        return jsonify({
            "status": "error",
            "message": "GraphRAG system not available"
        }), 500
    
    try:
        # Get the content from the request
        data = request.json
        content = data.get('content', '').strip()
        filename = data.get('filename', f'document_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        file_type = data.get('file_type', 'text')
        
        if not content:
            return jsonify({
                "status": "error",
                "message": "No content provided"
            }), 400
        
        # Ensure the files directory exists
        os.makedirs(FILES_DIRECTORY, exist_ok=True)
        
        # Handle different file types
        if file_type == 'pdf':
            # Save PDF file from base64
            import base64
            pdf_data = content.split(',')[1] if ',' in content else content
            file_path = os.path.join(FILES_DIRECTORY, filename)
            
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(pdf_data))
            
            print(f"📄 Saved PDF file: {filename}")
            
        elif file_type == 'docx':
            # Save DOCX file from base64
            import base64
            docx_data = content.split(',')[1] if ',' in content else content
            file_path = os.path.join(FILES_DIRECTORY, filename)
            
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(docx_data))
            
            print(f"📄 Saved DOCX file: {filename}")
            
        else:
            # Save text content to a file
            file_path = os.path.join(FILES_DIRECTORY, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 Saved text file: {filename}")
        
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
        print(f"❌ Error adding document: {e}")
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
        
        # Handle different response formats
        if isinstance(answer, dict):
            answer_text = answer.get('result', answer.get('answer', str(answer)))
        else:
            answer_text = str(answer)
        
        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer_text,
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
    
    if tracker is None or not hasattr(tracker, 'processed_files'):
        return jsonify({
            "status": "success",
            "documents": [],
            "total": 0
        })
    
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
    print("🔗 Application will be available at: http://localhost:5001")
    
    # Try to initialize the GraphRAG system
    if initialize_graphrag():
        print("🎉 Ready to go! Open http://localhost:5001 in your browser")
    else:
        print("⚠️  GraphRAG system not initialized, but server will start anyway")
        print("💡 Try adding some documents first!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)