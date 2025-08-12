import os
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# Set up base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define all the directories (like telling where each room is!)
STORAGE_DIRECTORY = os.path.join(BASE_DIR, "core", "storage")  # ← THIS WAS MISSING!
FILES_DIRECTORY = os.path.join(BASE_DIR, "core", "files")
TRACKING_FILE = os.path.join(STORAGE_DIRECTORY, "document_tracking.json")
EMBEDDING_CACHE_FILE = os.path.join(STORAGE_DIRECTORY, "embedding_cache.json")
CHROMADB_PERSIST_DIRECTORY = os.path.join(STORAGE_DIRECTORY, "chromadb")
CHROMADB_COLLECTION_NAME = "documents"

# Create directories if they don't exist (like making the rooms if they're not there)
os.makedirs(STORAGE_DIRECTORY, exist_ok=True)
os.makedirs(FILES_DIRECTORY, exist_ok=True)