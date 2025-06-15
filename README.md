# Enhanced Knowledge Graph RAG System with AstraDB

This enhanced Python script creates a sophisticated knowledge graph-based Retrieval-Augmented Generation (RAG) system that integrates AstraDB for persistent vector storage, Neo4j for graph databases, and implements intelligent document tracking to prevent redundant processing.

## 🚀 Key Features

### ✅ Implemented Enhancements

1. **Document Tracking System**: Prevents recreation of embeddings for unchanged documents using SHA256 hashing
2. **AstraDB Integration**: Replaces InMemoryVectorStore with persistent AstraDB storage
3. **Incremental Processing**: Only processes new or modified documents
4. **Robust Error Handling**: Comprehensive error handling throughout the pipeline
5. **Scalable Architecture**: Optimized for large document sets with batch processing
6. **Command-line Interface**: Flexible execution options with argument parsing

### 🏗️ System Architecture

```
Documents (.docx) → Document Tracker → Semantic Chunking → AstraDB Vector Store
                                     ↓
Knowledge Graph ← Neo4j Database ← LLM Graph Transformer
                                     ↓
GraphRetriever ← Vector Store + Knowledge Graph → RAG Chain → LLM Response
```

## 📋 Prerequisites

### Required Dependencies

```bash
pip install langchain_core langchain_google_genai langchain_neo4j langchain_community 
pip install langchain_experimental langchain_astradb astrapy graph_retriever
```

### Environment Setup

1. **Google AI API Key** (for embeddings and LLM):
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   ```

2. **Neo4j Database**:
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USERNAME="neo4j"
   export NEO4J_PASSWORD="your-password"
   ```

3. **AstraDB Credentials** (DataStax Astra DB):
   ```bash
   export ASTRA_DB_API_ENDPOINT="your-astra-db-endpoint"
   export ASTRA_DB_APPLICATION_TOKEN="your-astra-db-token"
   ```

## 🔧 Configuration

### AstraDB Setup

1. Create a DataStax Astra DB account at [astra.datastax.com](https://astra.datastax.com)
2. Create a new database and get your API endpoint
3. Generate an application token with appropriate permissions
4. Set the environment variables as shown above

### File Structure

```
wolfia/
├── files/                          # Place your .docx files here
│   ├── document1.docx
│   ├── document2.docx
│   └── ...
├── main_with_llmgraphtranformer.py  # Enhanced main script
├── document_tracking.json          # Auto-generated tracking file
└── logs/                           # Optional log directory
```

## 🚀 Usage

### Basic Usage

```bash
# First run - processes all documents
python main_with_llmgraphtranformer.py

# Subsequent runs - only processes new/changed documents
python main_with_llmgraphtranformer.py
```

### Advanced Options

```bash
# Force reprocess all documents (ignores tracking)
python main_with_llmgraphtranformer.py --force-reprocess

# Clean Neo4j database before processing
python main_with_llmgraphtranformer.py --clean-neo4j

# Only run tests (skip document processing)
python main_with_llmgraphtranformer.py --test-only

# Combine options
python main_with_llmgraphtranformer.py --force-reprocess --clean-neo4j
```

## 🔍 How It Works

### 1. Document Tracking System

The `DocumentTracker` class maintains a JSON file (`document_tracking.json`) that stores:
- File paths and SHA256 hashes
- Processing timestamps
- Chunk counts and file metadata

```json
{
  "documents": {
    "/path/to/document.docx": {
      "hash": "sha256-hash",
      "processed_at": "2024-01-01T12:00:00.000Z",
      "chunk_count": 15,
      "file_size": 1024000
    }
  },
  "last_updated": "2024-01-01T12:00:00.000Z"
}
```

### 2. Incremental Processing Pipeline

1. **Document Analysis**: Check each .docx file against tracking data
2. **Hash Comparison**: Calculate SHA256 hash to detect changes
3. **Selective Processing**: Only process new/changed documents
4. **Update Tracking**: Record processed documents with metadata

### 3. AstraDB Integration

- **Persistent Storage**: Documents are stored permanently in AstraDB
- **Incremental Updates**: New documents are added to existing collections
- **Metadata Queries**: Support for complex metadata-based retrieval
- **Scalability**: Handles large document collections efficiently

### 4. Error Handling

- **Connection Resilience**: Graceful handling of database connection issues
- **Processing Continuity**: System continues even if individual documents fail
- **Fallback Mechanisms**: Falls back to basic retrieval if GraphRetriever fails
- **Detailed Logging**: Comprehensive error reporting and progress tracking

## 📊 Monitoring and Debugging

### Tracking File Analysis

The `document_tracking.json` file provides insights into:
- Which documents have been processed
- When they were last processed
- How many chunks were created
- File modification detection

### System Statistics

The system reports:
- Number of documents processed vs. skipped
- Neo4j node and relationship counts
- Vector store status and document counts
- Processing times and error rates

## 🔧 Troubleshooting

### Common Issues

1. **AstraDB Connection Failed**
   - Verify ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN
   - Check network connectivity
   - Ensure token has sufficient permissions

2. **Neo4j Connection Issues**
   - Verify Neo4j is running
   - Check connection parameters
   - Ensure user has write permissions

3. **Document Processing Errors**
   - Verify .docx files are not corrupted
   - Check file permissions
   - Ensure sufficient disk space

4. **Memory Issues with Large Documents**
   - Use `--force-reprocess` sparingly
   - Process documents in smaller batches
   - Monitor system memory usage

### Debug Mode

To enable detailed logging, modify the script to include:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Performance Optimization

### For Large Document Sets

1. **Batch Processing**: Documents are processed individually to optimize memory usage
2. **Selective Updates**: Only changed documents trigger graph updates
3. **Efficient Hashing**: SHA256 calculation is optimized with chunked reading
4. **Connection Pooling**: Database connections are reused efficiently

### Recommended Settings

- **Process documents in batches** of 50-100 for very large collections
- **Use incremental mode** for regular updates
- **Clean Neo4j database** only when necessary
- **Monitor AstraDB quotas** to avoid rate limiting

## 📝 Sample Usage Scenarios

### Initial Setup
```bash
# First time setup with all documents
python main_with_llmgraphtranformer.py --clean-neo4j
```

### Daily Updates
```bash
# Regular operation - only processes new/changed files
python main_with_llmgraphtranformer.py
```

### Major Rebuild
```bash
# Complete reprocessing when needed
python main_with_llmgraphtranformer.py --force-reprocess --clean-neo4j
```

### Testing Only
```bash
# Test the system without processing documents
python main_with_llmgraphtranformer.py --test-only
```

## 🔐 Security Considerations

- Store API keys and tokens as environment variables
- Use secure connections to databases
- Implement proper access controls for AstraDB
- Regular backup of tracking data and configurations
- Monitor API usage and costs

## 📈 Future Enhancements

The system is designed to be extensible:
- Support for additional document formats
- Advanced metadata filtering
- Custom embedding models
- Distributed processing capabilities
- Real-time document monitoring
- Advanced graph traversal strategies

---

For questions or issues, please refer to the error messages and logs for detailed information about any problems encountered during processing. 