#!/usr/bin/env python3
"""
Enhanced Knowledge Graph RAG System with LLMGraphTransformer
This version includes document tracking, embedding cache, and flexible vector storage.
FIXED: Disabled enhanced_schema to avoid APOC dependency issues
"""

import os
import sys
import argparse
from typing import List, Optional, Tuple
from pathlib import Path

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Import core dependencies
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain, Neo4jVector
from langchain_community.document_loaders import Docx2txtLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_experimental.graph_transformers import LLMGraphTransformer

# Import custom modules
from core.embedding_cache import EmbeddingCache
from core.document_tracker import DocumentTracker
from core.config import FILES_DIRECTORY, STORAGE_DIRECTORY

# Check for ChromaDB availability
CHROMADB_AVAILABLE = False
try:
    from langchain_community.vectorstores import Chroma
    import chromadb
    CHROMADB_AVAILABLE = True
    print("✅ ChromaDB is available for persistent storage")
except ImportError:
    print("ℹ️ ChromaDB not available. Using in-memory vector store.")
    from langchain_community.vectorstores import InMemoryVectorStore

# Initialize components
print("🔄 Initializing components...")

# Embedding cache initialization
embedding_cache = EmbeddingCache()
# Fix: Use the correct attribute name (could be _cache, data, or embeddings)
try:
    cache_size = len(embedding_cache._cache) if hasattr(embedding_cache, '_cache') else 0
except:
    cache_size = 0
print(f"Loaded embedding cache with {cache_size} entries")

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
    
    # Find all .docx files
    docx_files = list(Path(FILES_DIRECTORY).glob("*.docx"))
    
    # Also support .txt files
    txt_files = list(Path(FILES_DIRECTORY).glob("*.txt"))
    
    all_files = docx_files + txt_files
    
    if not all_files:
        print(f"⚠️ No .docx or .txt files found in {FILES_DIRECTORY}")
        return documents, processed_files
    
    print(f"📂 Found {len(all_files)} files to process")
    
    for file_path in all_files:
        file_str = str(file_path)
        
        # Check if file needs processing
        if not force_reprocess and tracker.is_processed(file_str):
            print(f"⏩ Skipping already processed: {file_path.name}")
            skipped_files.append(file_str)
            # Load from existing vector store instead of skipping entirely
            continue
        
        print(f"📄 Processing: {file_path.name}")
        
        try:
            # Load document based on file type
            if file_path.suffix == '.docx':
                loader = Docx2txtLoader(file_str)
                docs = loader.load()
            else:  # .txt file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                docs = [Document(page_content=content, metadata={"source": file_str})]
            
            # Process each document
            for doc in docs:
                # Use semantic chunker for better results
                text_splitter = SemanticChunker(
                    embeddings=base_embeddings,
                    breakpoint_threshold_type="percentile",
                    breakpoint_threshold_amount=70
                )
                
                chunks = text_splitter.split_documents([doc])
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

def initialize_vector_store(documents: List[Document], use_chromadb: bool = None):
    """Initialize vector store with documents"""
    if not documents:
        print("⚠️ No documents to add to vector store")
        return None
    
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
    """Setup RAG chain with vector store and graph"""
    from langchain.chains import RetrievalQA
    from langchain_core.prompts import PromptTemplate
    
    # Create a custom prompt template
    prompt_template = """You are an assistant that provides accurate answers based on the provided context.
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
    Always cite the source of your information when possible.

    Context:
    {context}

    Question: {question}

    Answer: """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Setup retrieval QA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    
    print("✅ RAG chain with simple retrieval configured")
    return chain

def test_system(chain, graph: Neo4jGraph):
    """Test the system with sample queries"""
    print("\n" + "="*50)
    print("🧪 TESTING THE SYSTEM")
    print("="*50)
    
    # Test Neo4j connection with a simple query
    try:
        # FIXED: Use a simple query that doesn't require APOC
        result = graph.query("MATCH (n) RETURN count(n) as count LIMIT 1")
        print(f"✅ Neo4j connection successful. Nodes in graph: {result[0]['count'] if result else 0}")
    except Exception as e:
        print(f"⚠️ Neo4j query error: {e}")
    
    if not chain:
        print("⚠️ No chain available for testing")
        return
    
    test_queries = [
        "What are the main topics discussed in the documents?",
        "Summarize the key points from the knowledge base.",
        "What entities or concepts are mentioned most frequently?"
    ]
    
    for query in test_queries[:1]:  # Test with just one query
        print(f"\n📝 Query: {query}")
        try:
            response = chain.invoke({"query": query})
            answer = response.get('result', 'No answer found')
            print(f"💡 Answer: {answer[:500]}...")  # Truncate long answers
        except Exception as e:
            print(f"❌ Error during query: {e}")

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
        
        if documents or tracker.processed_files:
            # Initialize vector store
            vector_store = initialize_vector_store(documents, use_chromadb)
            
            # Create knowledge graph only for newly processed documents
            if documents:
                create_knowledge_graph(documents, graph)
            
            # Setup RAG chain
            if vector_store:
                chain = setup_rag_chain(vector_store, graph)
        else:
            print("⚠️ No documents found or processed. Add .docx or .txt files to 'core/files/' directory")
    
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