#!/usr/bin/env python3
"""
Enhanced Knowledge Graph RAG System with LLMGraphTransformer
This version includes document tracking, embedding cache, and flexible vector storage.
FIXED: Added missing imports and corrected vector store handling
"""

import os
import sys
import argparse
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Import core dependencies
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph
from langchain_community.document_loaders import Docx2txtLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_experimental.graph_transformers import LLMGraphTransformer

# FIXED: Added missing vector store imports
from langchain_core.vectorstores import InMemoryVectorStore

# Import custom modules - Fixed import paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.embedding_cache import EmbeddingCache
    from core.document_tracker import DocumentTracker
    from core.config import FILES_DIRECTORY, STORAGE_DIRECTORY
except ImportError:
    # Fallback for running from project root
    from embedding_cache import EmbeddingCache
    from document_tracker import DocumentTracker
    from config import FILES_DIRECTORY, STORAGE_DIRECTORY

# Check for ChromaDB availability
CHROMADB_AVAILABLE = False
try:
    from langchain_community.vectorstores import Chroma
    import chromadb
    CHROMADB_AVAILABLE = True
    print("✅ ChromaDB is available for persistent storage")
except ImportError:
    print("ℹ️ ChromaDB not available. Using in-memory vector store.")

# Initialize components
print("🔄 Initializing components...")

# Embedding cache initialization
embedding_cache = EmbeddingCache()
# Fix: Use the correct attribute name (could be _cache, data, or embeddings)
try:
    cache_size = len(embedding_cache._cache) if hasattr(embedding_cache, '_cache') else 0
except:
    cache_size = 0
print(f"📦 Loaded {cache_size} cached embeddings")

# Cached embeddings wrapper
class CachedEmbeddings:
    def __init__(self, base_embeddings, cache):
        self.base_embeddings = base_embeddings
        self.cache = cache
    
    def embed_documents(self, texts):
        """Embed documents with caching"""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache first
        for i, text in enumerate(texts):
            cached = self.cache.get_embedding(text)
            if cached is not None:
                embeddings.append(cached)
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.base_embeddings.embed_documents(uncached_texts)
            for text, embedding, idx in zip(uncached_texts, new_embeddings, uncached_indices):
                self.cache.add_embedding(text, embedding)
                embeddings[idx] = embedding
        
        return embeddings
    
    def embed_query(self, text):
        """Embed query with caching"""
        cached = self.cache.get_embedding(text)
        if cached is not None:
            return cached
        
        embedding = self.base_embeddings.embed_query(text)
        self.cache.add_embedding(text, embedding)
        return embedding

# Initialize base embeddings and wrap with cache
base_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings = CachedEmbeddings(base_embeddings, embedding_cache)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
print("✅ Successfully initialized cached embeddings and LLM")

# Environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def check_environment():
    """Check if all required environment variables are set"""
    missing = []
    if not os.getenv("GOOGLE_API_KEY"):
        missing.append("GOOGLE_API_KEY")
    if not NEO4J_PASSWORD or NEO4J_PASSWORD == "password":
        missing.append("NEO4J_PASSWORD (using default)")
    
    if missing:
        print("⚠️ Missing or default environment variables:", ", ".join(missing))
        return False
    return True

def check_chromadb_availability():
    """Check if ChromaDB is properly installed and available"""
    return CHROMADB_AVAILABLE

def clean_neo4j_database(graph: Neo4jGraph):
    """Clean all nodes and relationships from Neo4j database"""
    try:
        print("🧹 Cleaning Neo4j database...")
        graph.query("MATCH (n) DETACH DELETE n")
        print("✅ Neo4j database cleaned")
    except Exception as e:
        print(f"⚠️ Could not clean database: {e}")

def load_and_process_documents(tracker: DocumentTracker, force_reprocess: bool = False) -> Tuple[List[Document], List[str]]:
    """Load documents from files directory with tracking"""
    documents = []
    processed_files = []
    skipped_files = []
    
    # Ensure files directory exists
    os.makedirs(FILES_DIRECTORY, exist_ok=True)
    
    # Find all supported files
    supported_extensions = ["*.docx", "*.pdf", "*.txt"]
    all_files = []
    
    for extension in supported_extensions:
        all_files.extend(list(Path(FILES_DIRECTORY).glob(extension)))
    
    if not all_files:
        print(f"⚠️ No supported files (.docx, .pdf, .txt) found in {FILES_DIRECTORY}")
        return documents, processed_files
    
    print(f"📂 Found {len(all_files)} files to process")
    
    for file_path in all_files:
        file_str = str(file_path)
        
        # Check if file needs processing
        if not force_reprocess and tracker.is_processed(file_str):
            print(f"⏩ Skipping already processed: {file_path.name}")
            skipped_files.append(file_str)
            continue
        
        print(f"📄 Processing: {file_path.name}")
        
        try:
            # Load document based on file type
            if file_path.suffix.lower() == '.docx':
                loader = Docx2txtLoader(file_str)
                docs = loader.load()
            elif file_path.suffix.lower() == '.pdf':
                # For PDF files, use PyMuPDF or pdfplumber for better extraction
                try:
                    # Try pdfplumber first
                    try:
                        import pdfplumber
                        content = ""
                        with pdfplumber.open(file_path) as pdf:
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    content += page_text + "\n"
                        docs = [Document(page_content=content, metadata={"source": file_str})]
                    except ImportError:
                        # Fallback to PyMuPDF
                        try:
                            import fitz  # PyMuPDF
                            content = ""
                            pdf_document = fitz.open(file_path)
                            for page_num in range(pdf_document.page_count):
                                page = pdf_document[page_num]
                                content += page.get_text() + "\n"
                            pdf_document.close()
                            docs = [Document(page_content=content, metadata={"source": file_str})]
                        except ImportError:
                            print(f"  ⚠️ PDF processing requires pdfplumber or PyMuPDF. Install with:")
                            print(f"     pip install pdfplumber")
                            print(f"  Skipping: {file_path.name}")
                            continue
                except Exception as e:
                    print(f"  ⚠️ Error processing PDF {file_path.name}: {e}")
                    continue
            else:  # .txt file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                docs = [Document(page_content=content, metadata={"source": file_str})]
            
            # Process each document with enhanced chunking
            for doc in docs:
                # Use semantic chunker with optimized settings for research documents
                text_splitter = SemanticChunker(
                    embeddings=base_embeddings,
                    breakpoint_threshold_type="percentile",
                    breakpoint_threshold_amount=60,  # More sensitive to create richer chunks
                    number_of_chunks=None  # Let it determine optimal chunking
                )
                
                chunks = text_splitter.split_documents([doc])
                
                # Enhance chunk metadata with additional context
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        "source_file": os.path.basename(file_str),
                        "file_path": file_str,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "processed_at": datetime.now().isoformat(),
                        "document_type": file_path.suffix.lower()[1:]  # pdf, docx, txt
                    })
                
                documents.extend(chunks)
                
                # Track the processed file
                tracker.mark_processed(file_str, len(chunks))
                processed_files.append(file_str)
                
                print(f"  ✅ Created {len(chunks)} chunks")
                
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
    
    # Save tracking data
    tracker.save()
    
    print(f"\n📊 Processing Summary:")
    print(f"  - Processed: {len(processed_files)} files")
    print(f"  - Skipped: {len(skipped_files)} files") 
    print(f"  - Total chunks: {len(documents)}")
    
    return documents, processed_files

def create_enhanced_knowledge_graph(documents: List[Document], graph: Neo4jGraph):
    """Create enhanced knowledge graph with better entity extraction"""
    if not documents:
        print("⚠️ No documents to add to knowledge graph")
        return
    
    print("🔄 Creating enhanced knowledge graph using LLMGraphTransformer...")
    
    # Initialize enhanced LLMGraphTransformer with research-specific entities
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=[
            "Person", "Researcher", "Author", 
            "Organization", "Institution", 
            "Location", "Country", "Population",
            "Concept", "Theory", "Method", "Technique",
            "Study", "Research", "Intervention",
            "Outcome", "Finding", "Result",
            "Trauma", "Recovery", "Therapy",
            "Family", "Relationship", "Child",
            "Narrative", "Approach", "Strategy"
        ],
        allowed_relationships=[
            "AUTHORED", "CONDUCTED", "STUDIED", "RESEARCHED",
            "FOUND", "DISCOVERED", "REPORTED", "CONCLUDED",
            "USED", "APPLIED", "IMPLEMENTED", "DEVELOPED",
            "RELATES_TO", "CONNECTED_TO", "INFLUENCES", "AFFECTS",
            "MENTIONS", "DISCUSSES", "DESCRIBES", "EXPLAINS",
            "PARTICIPATES_IN", "BELONGS_TO", "PART_OF",
            "TREATS", "HELPS", "SUPPORTS", "IMPROVES"
        ],
        node_properties=["description", "type", "context"],
        relationship_properties=["description", "strength", "context"]
    )
    
    # Process documents in smaller batches for better quality
    batch_size = 3  # Smaller batches for more detailed processing
    total_nodes = 0
    total_relationships = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")
        
        try:
            # Convert documents to graph documents
            graph_documents = llm_transformer.convert_to_graph_documents(batch)
            
            # Count entities
            for graph_doc in graph_documents:
                total_nodes += len(graph_doc.nodes)
                total_relationships += len(graph_doc.relationships)
            
            # Add to Neo4j with enhanced labeling
            graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
            
        except Exception as e:
            print(f"  ⚠️ Error processing batch {i//batch_size + 1}: {e}")
            continue
    
    print(f"✅ Enhanced knowledge graph created with {total_nodes} nodes and {total_relationships} relationships")
    
    # Create additional indexes for better performance
    try:
        graph.query("CREATE INDEX entity_name_index IF NOT EXISTS FOR (n:__Entity__) ON (n.id)")
        graph.query("CREATE INDEX document_source_index IF NOT EXISTS FOR (n:Document) ON (n.source)")
        print("✅ Created performance indexes")
    except Exception as e:
        print(f"⚠️ Could not create indexes: {e}")

def create_knowledge_graph(documents: List[Document], graph: Neo4jGraph):
    """Wrapper for backward compatibility"""
    return create_enhanced_knowledge_graph(documents, graph)

def initialize_vector_store(documents: List[Document], use_chromadb: bool = None):
    """Initialize vector store with documents"""
    if not documents:
        print("💾 Using in-memory vector store...")
        return InMemoryVectorStore(embeddings)
    
    # Auto-detect ChromaDB if not specified
    if use_chromadb is None:
        use_chromadb = CHROMADB_AVAILABLE
    
    if use_chromadb and CHROMADB_AVAILABLE:
        print("🗄️ Using ChromaDB for persistent storage...")
        persist_directory = os.path.join(STORAGE_DIRECTORY, "chromadb")
        os.makedirs(persist_directory, exist_ok=True)
        
        vector_store = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory=persist_directory,
            collection_name="knowledge_graph_docs"
        )
        print(f"✅ ChromaDB initialized with {len(documents)} documents")
    else:
        print("💾 Using in-memory vector store...")
        vector_store = InMemoryVectorStore.from_documents(
            documents,
            embeddings
        )
        print(f"✅ In-memory store initialized with {len(documents)} documents")
    
    return vector_store

def create_knowledge_graph(documents: List[Document], graph: Neo4jGraph):
    """Create knowledge graph from documents using LLMGraphTransformer"""
    if not documents:
        print("⚠️ No documents to add to knowledge graph")
        return
    
    print("🔄 Creating knowledge graph using LLMGraphTransformer...")
    
    # Initialize the LLMGraphTransformer
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Person", "Organization", "Location", "Technology", "Concept", "Policy", "System"],
        allowed_relationships=["MENTIONS", "RELATES_TO", "MANAGES", "IMPLEMENTS", "REQUIRES", "APPROVES", "USES"],
        node_properties=["description"],
        relationship_properties=["description"]
    )
    
    # Process documents in batches for better performance
    batch_size = 5
    total_nodes = 0
    total_relationships = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")
        
        try:
            # Convert documents to graph documents
            graph_documents = llm_transformer.convert_to_graph_documents(batch)
            
            # Count entities
            for graph_doc in graph_documents:
                total_nodes += len(graph_doc.nodes)
                total_relationships += len(graph_doc.relationships)
            
            # Add to Neo4j
            graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
            
        except Exception as e:
            print(f"  ⚠️ Error processing batch: {e}")
            continue
    
    print(f"✅ Knowledge graph created with approximately {total_nodes} nodes and {total_relationships} relationships")

def setup_rag_chain(vector_store, graph: Neo4jGraph):
    """Setup enhanced RAG chain with comprehensive retrieval and smart synthesis"""
    from langchain.chains import RetrievalQA
    from langchain_core.prompts import PromptTemplate
    
    # Create an enhanced prompt template for intelligent responses
    prompt_template = """You are an expert research assistant with access to a comprehensive knowledge base about research methodologies and writing. Your task is to provide detailed, insightful responses based on the available documents.

Context from the knowledge base:
{context}

Question: {question}

Instructions:
- Provide comprehensive, detailed answers that synthesize information across the documents
- Draw connections between different concepts and studies mentioned
- Include specific details, methodologies, findings, and insights from the research
- When citing information, be specific about which studies or approaches are being referenced
- If multiple perspectives exist, discuss them
- Provide practical implications when relevant
- Write in an academic but accessible style suitable for literature reviews

Answer: """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Setup enhanced retrieval with more comprehensive search
    enhanced_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 10,  # Retrieve more documents for comprehensive answers
            "fetch_k": 20  # Consider more documents initially
        }
    )
    
    # Setup enhanced retrieval QA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Use "stuff" to include all context
        retriever=enhanced_retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
        verbose=False
    )
    
    print("✅ Enhanced RAG chain with comprehensive retrieval configured")
    return chain

def create_graph_enhanced_retriever(vector_store, graph: Neo4jGraph):
    """Create a retriever that combines vector similarity with graph relationships"""
    class GraphEnhancedRetriever:
        def __init__(self, vector_store, graph):
            self.vector_store = vector_store
            self.graph = graph
            self.base_retriever = vector_store.as_retriever(
                search_kwargs={"k": 8}
            )
        
        def get_relevant_documents(self, query: str):
            # Get initial documents from vector similarity
            docs = self.base_retriever.get_relevant_documents(query)
            
            # Try to enhance with graph relationships
            try:
                # Extract key entities from the query using the graph
                graph_query = f"""
                MATCH (n:__Entity__)
                WHERE n.id CONTAINS toLower('{query}') OR n.id CONTAINS 'trauma' OR n.id CONTAINS 'family' OR n.id CONTAINS 'narrative'
                RETURN n.id as entity, n.description as description
                LIMIT 5
                """
                
                graph_results = self.graph.query(graph_query)
                
                if graph_results:
                    # Add graph context to the documents
                    graph_context = "\\n\\nRelated concepts from knowledge graph:\\n"
                    for result in graph_results:
                        if result.get('entity') and result.get('description'):
                            graph_context += f"- {result['entity']}: {result['description']}\\n"
                    
                    # Enhance the first document with graph context
                    if docs and graph_context.strip():
                        enhanced_doc = docs[0]
                        enhanced_doc.page_content += graph_context
                        
            except Exception as e:
                print(f"Graph enhancement failed: {e}")
            
            return docs
    
    return GraphEnhancedRetriever(vector_store, graph)

def test_system(chain, graph: Neo4jGraph):
    """Test the system with comprehensive queries"""
    print("\n" + "="*50)
    print("🧪 TESTING THE ENHANCED SYSTEM")
    print("="*50)
    
    # Test Neo4j connection with detailed statistics
    try:
        node_result = graph.query("MATCH (n) RETURN count(n) as count")
        rel_result = graph.query("MATCH ()-[r]->() RETURN count(r) as rel_count")
        entity_result = graph.query("MATCH (n:__Entity__) RETURN count(n) as entity_count")
        
        total_nodes = node_result[0]['count'] if node_result else 0
        total_rels = rel_result[0]['rel_count'] if rel_result else 0
        entity_count = entity_result[0]['entity_count'] if entity_result else 0
        
        print(f"✅ Neo4j connection successful:")
        print(f"   📊 Total nodes: {total_nodes}")
        print(f"   🔗 Total relationships: {total_rels}")
        print(f"   🏷️ Entities: {entity_count}")
        
        # Show some sample entities
        try:
            sample_entities = graph.query("MATCH (n:__Entity__) RETURN n.id as entity LIMIT 5")
            if sample_entities:
                print(f"   🎯 Sample entities: {[e['entity'] for e in sample_entities]}")
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Neo4j query error: {e}")
    
    if not chain:
        print("⚠️ No chain available for testing")
        return
    
    # Test with research-specific queries
    test_queries = [
        "What are the main methodological approaches discussed in trauma research?",
        "How do narrative methods contribute to understanding family relationships?",
        "What are the key findings about trauma recovery mentioned in the documents?"
    ]
    
    print(f"\n🔍 Testing enhanced retrieval with {len(test_queries)} queries:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        try:
            response = chain.invoke({"query": query})
            answer = response.get('result', 'No answer found')
            
            # Show a meaningful portion of the answer
            if len(answer) > 200:
                print(f"💡 Answer: {answer[:400]}...")
                print(f"   📏 Full answer length: {len(answer)} characters")
            else:
                print(f"💡 Answer: {answer}")
                
            # Show source count if available
            sources = response.get('source_documents', [])
            if sources:
                print(f"   📚 Used {len(sources)} source documents")
                
        except Exception as e:
            print(f"❌ Error during query {i}: {e}")
    
    print(f"\n✅ Enhanced system testing complete!")
    print(f"🎯 The system should now provide comprehensive, intelligent answers!")

def main(force_reprocess=False, clean_neo4j=False, use_chromadb=None, test_only=False):
    """Main execution function"""
    print("\n🚀 Starting Enhanced Knowledge Graph RAG System")
    print("="*50)
    
    # Check environment
    if not check_environment():
        print("⚠️ Please set missing environment variables")
    
    # Initialize document tracker
    tracker = DocumentTracker()
    print(f"📊 Tracker: {len(tracker.processed_files)} files previously processed")
    
    # Initialize Neo4j connection with enhanced_schema DISABLED
    try:
        # IMPORTANT FIX: Set enhanced_schema=False to avoid APOC dependency
        graph = Neo4jGraph(
            url=NEO4J_URI, 
            username=NEO4J_USERNAME, 
            password=NEO4J_PASSWORD,
            enhanced_schema=False  # This disables APOC requirement
        )
        print("✅ Connected to Neo4j successfully (APOC not required)")
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {e}")
        print("\n💡 Tip: Make sure Neo4j is running and credentials are correct")
        return None, None, None
    
    # Clean database if requested
    if clean_neo4j:
        clean_neo4j_database(graph)
    
    # Initialize variables
    vector_store = None
    chain = None
    
    if not test_only:
        # Process documents
        documents, processed_files = load_and_process_documents(tracker, force_reprocess)
        
        # ALWAYS initialize vector store, even if no new documents
        if documents or tracker.processed_files:
            if documents:
                # New documents to process
                vector_store = initialize_vector_store(documents, use_chromadb)
                
                # Create knowledge graph only for newly processed documents
                create_enhanced_knowledge_graph(documents, graph)
            else:
                # No new documents, but load existing vector store
                print("📚 Loading existing vector store...")
                if use_chromadb and CHROMADB_AVAILABLE:
                    persist_directory = os.path.join(STORAGE_DIRECTORY, "chromadb")
                    if os.path.exists(persist_directory):
                        from langchain_community.vectorstores import Chroma
                        vector_store = Chroma(
                            embedding_function=embeddings,
                            persist_directory=persist_directory,
                            collection_name="knowledge_graph_docs"
                        )
                        print("✅ Loaded existing ChromaDB vector store")
                    else:
                        print("⚠️ No existing ChromaDB found, creating empty store")
                        vector_store = initialize_vector_store([], use_chromadb)
                else:
                    # For in-memory, we need to reprocess to load data
                    print("💭 In-memory store requires reprocessing...")
                    all_files = list(Path(FILES_DIRECTORY).glob("*.pdf")) + list(Path(FILES_DIRECTORY).glob("*.docx")) + list(Path(FILES_DIRECTORY).glob("*.txt"))
                    if all_files:
                        print("🔄 Reprocessing documents for in-memory store...")
                        documents, _ = load_and_process_documents(tracker, force_reprocess=True)
                        vector_store = initialize_vector_store(documents, use_chromadb)
                    else:
                        vector_store = initialize_vector_store([], use_chromadb)
            
            # Setup RAG chain
            if vector_store:
                chain = setup_rag_chain(vector_store, graph)
                
                # Verify vector store has documents
                try:
                    if hasattr(vector_store, '_collection'):
                        doc_count = vector_store._collection.count()
                        print(f"📊 Vector store contains {doc_count} document chunks")
                    elif hasattr(vector_store, 'docstore'):
                        doc_count = len(vector_store.docstore._dict)
                        print(f"📊 Vector store contains {doc_count} document chunks")
                except:
                    print("📊 Vector store initialized (count unavailable)")
        else:
            print("⚠️ No documents found or processed. Add .docx, .pdf, or .txt files to 'core/files/' directory")
    
    # Test the system
    test_system(chain, graph)
    
    # Save cache
    embedding_cache.save()
    # Fix: Use the correct attribute name
    try:
        cache_size = len(embedding_cache._cache) if hasattr(embedding_cache, '_cache') else 0
    except:
        cache_size = 0
    
    print(f"\n💾 Saved embedding cache with {cache_size} entries")
    
    print("\n✅ System ready for queries!")
    return chain, vector_store, graph

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Knowledge Graph RAG System")
    parser.add_argument("--force-reprocess", action="store_true", help="Force reprocess all documents")
    parser.add_argument("--clean-neo4j", action="store_true", help="Clean Neo4j database before processing")
    parser.add_argument("--use-chromadb", action="store_true", help="Use ChromaDB for vector storage")
    parser.add_argument("--use-memory", action="store_true", help="Use in-memory vector storage")
    parser.add_argument("--test-only", action="store_true", help="Only run tests, skip document processing")
    
    args = parser.parse_args()
    
    # Determine vector store preference
    use_chromadb = None
    if args.use_chromadb:
        use_chromadb = True
    elif args.use_memory:
        use_chromadb = False
    
    main(
        force_reprocess=args.force_reprocess,
        clean_neo4j=args.clean_neo4j,
        use_chromadb=use_chromadb,
        test_only=args.test_only
    )