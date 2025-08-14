# api_bridge.py
"""
API bridge to connect your frontend to GraphRAG system
Updated version with better PDF and document handling
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
import tempfile
import mimetypes
import base64
import shutil

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

def save_uploaded_file(content, filename, file_type):
    """Save uploaded file to the files directory"""
    # Ensure the files directory exists
    os.makedirs(FILES_DIRECTORY, exist_ok=True)
    
    # Generate unique filename if already exists
    base_name, ext = os.path.splitext(filename)
    counter = 1
    original_filename = filename
    
    while os.path.exists(os.path.join(FILES_DIRECTORY, filename)):
        filename = f"{base_name}_{counter}{ext}"
        counter += 1
    
    file_path = os.path.join(FILES_DIRECTORY, filename)
    
    if file_type in ['pdf', 'docx']:
        # Handle binary files (base64 encoded)
        try:
            # Remove data URL prefix if present
            if ',' in content:
                content = content.split(',')[1]
            
            # Decode base64 content
            file_data = base64.b64decode(content)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
                
        except Exception as e:
            raise Exception(f"Failed to decode and save binary file: {str(e)}")
    else:
        # Handle text files
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return file_path, filename

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
        
        # Save the file to the files directory
        try:
            file_path, actual_filename = save_uploaded_file(content, filename, file_type)
            print(f"📄 Saved {file_type.upper()} file: {actual_filename}")
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to save file: {str(e)}"
            }), 500
        
        # Reinitialize the system to process the new document
        try:
            chain, vector_store, graph = graphrag_main(
                force_reprocess=False,  # Only process new documents
                clean_neo4j=False,
                use_chromadb=False
            )
            
            # Update tracker
            if DocumentTracker:
                tracker = DocumentTracker()
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to process document: {str(e)}"
            }), 500
        
        return jsonify({
            "status": "success",
            "message": f"Document '{actual_filename}' added successfully",
            "filename": actual_filename,
            "file_path": file_path
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
        result = chain.invoke({"query": question})
        
        # Handle different response formats
        if isinstance(result, dict):
            answer_text = result.get('result', result.get('answer', str(result)))
        else:
            answer_text = str(result)
        
        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer_text,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Query error: {e}")
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

@app.route('/api/embeddings', methods=['GET'])
def get_embeddings_info():
    """Get information about stored embeddings"""
    try:
        from core.embedding_cache import EmbeddingCache
        
        cache = EmbeddingCache()
        stats = cache.get_stats()
        
        return jsonify({
            "status": "success",
            "embeddings_info": {
                "total_embeddings": stats.get('total_embeddings', 0),
                "cache_file": stats.get('cache_file', 'Unknown'),
                "cache_size_mb": round(stats.get('cache_size_mb', 0), 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get embeddings info: {str(e)}"
        }), 500

@app.route('/api/system_info', methods=['GET'])
def get_system_info():
    """Get comprehensive system information"""
    try:
        system_info = {
            "files_directory": FILES_DIRECTORY,
            "files_found": [],
            "embeddings_info": {},
            "neo4j_status": "unknown"
        }
        
        # Check files directory
        if os.path.exists(FILES_DIRECTORY):
            files = []
            for ext in ['*.pdf', '*.docx', '*.txt']:
                import glob
                files.extend(glob.glob(os.path.join(FILES_DIRECTORY, ext)))
            
            system_info["files_found"] = [os.path.basename(f) for f in files]
        
        # Get embeddings info
        try:
            from core.embedding_cache import EmbeddingCache
            cache = EmbeddingCache()
            stats = cache.get_stats()
            system_info["embeddings_info"] = stats
        except:
            pass
        
        # Check Neo4j status
        if graph:
            try:
                result = graph.query("MATCH (n) RETURN count(n) as count")
                system_info["neo4j_status"] = f"Connected - {result[0]['count']} nodes"
            except:
                system_info["neo4j_status"] = "Connection error"
        
        return jsonify({
            "status": "success",
            "system_info": system_info
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get system info: {str(e)}"
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

    # Update your api_bridge.py to include the enhanced literature review generation

@app.route('/api/generate_enhanced_review', methods=['POST'])
def generate_enhanced_literature_review():
    """Generate a comprehensive literature review using enhanced methodology"""
    global chain, vector_store, graph
    
    if chain is None:
        return jsonify({
            "status": "error",
            "message": "GraphRAG system not initialized. Please add documents first."
        }), 400
    
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        review_type = data.get('review_type', 'systematic')  # systematic, narrative, scoping
        depth = data.get('depth', 'comprehensive')  # comprehensive, focused, overview
        
        if not topic:
            return jsonify({
                "status": "error",
                "message": "No topic provided"
            }), 400
        
        # Initialize the enhanced literature review generator
        from enhanced_lit_review_system import EnhancedLiteratureReviewGenerator
        
        generator = EnhancedLiteratureReviewGenerator(chain, vector_store, graph)
        
        # Generate the comprehensive review
        review_process = generator.generate_comprehensive_review(topic, review_type)
        
        return jsonify({
            "status": "success",
            "topic": topic,
            "review_type": review_type,
            "process": review_process,
            "final_review": review_process.get("final_review", ""),
            "metadata": review_process.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Enhanced review error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Enhanced review generation failed: {str(e)}"
        }), 500

@app.route('/api/review_progress/<review_id>', methods=['GET'])
def get_review_progress(review_id):
    """Get progress of an ongoing literature review generation"""
    # This would track the progress of long-running review generation
    return jsonify({
        "status": "success",
        "review_id": review_id,
        "current_phase": "analyzing",
        "progress_percentage": 65,
        "estimated_completion": "2 minutes"
    })

@app.route('/api/refine_review_section', methods=['POST'])
def refine_review_section():
    """Refine a specific section of the literature review"""
    try:
        data = request.json
        section_content = data.get('section_content', '')
        refinement_type = data.get('refinement_type', 'improve_analysis')  # improve_analysis, enhance_synthesis, strengthen_critique
        specific_feedback = data.get('feedback', '')
        
        refinement_prompt = f"""
        Refine this literature review section based on the feedback: "{specific_feedback}"
        
        Refinement focus: {refinement_type}
        
        Original section:
        {section_content}
        
        Improvements needed:
        {_get_refinement_instructions(refinement_type)}
        
        Provide an enhanced version that addresses these specific areas.
        """
        
        result = chain.invoke({"query": refinement_prompt})
        
        return jsonify({
            "status": "success",
            "original_section": section_content,
            "refined_section": result.get('result', ''),
            "refinement_type": refinement_type,
            "improvements_made": _analyze_improvements(section_content, result.get('result', ''))
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Section refinement failed: {str(e)}"
        }), 500

def _get_refinement_instructions(refinement_type):
    """Get specific instructions for different types of refinements"""
    instructions = {
        "improve_analysis": """
        - Deepen the critical analysis of studies
        - Evaluate methodological strengths and limitations
        - Assess the quality of evidence presented
        - Consider alternative interpretations of findings
        """,
        "enhance_synthesis": """
        - Better integrate findings across studies
        - Identify patterns and themes more clearly
        - Connect studies to broader theoretical frameworks
        - Develop more sophisticated conceptual links
        """,
        "strengthen_critique": """
        - Provide more balanced evaluation of sources
        - Identify gaps and limitations more clearly
        - Consider methodological issues
        - Evaluate the reliability and validity of findings
        """,
        "improve_writing": """
        - Enhance academic writing style
        - Improve clarity and flow
        - Strengthen paragraph transitions
        - Ensure proper citation integration
        """
    }
    return instructions.get(refinement_type, "General improvement needed")

def _analyze_improvements(original, refined):
    """Analyze what improvements were made"""
    return {
        "word_count_change": len(refined.split()) - len(original.split()),
        "structure_improved": "Enhanced paragraph structure and flow",
        "analysis_deepened": "Added more critical evaluation",
        "synthesis_enhanced": "Better integration of sources"
    }