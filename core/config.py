import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

# ADD THIS LINE - it was missing!
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRACKING_FILE = os.path.join(BASE_DIR, "core", "storage", "document_tracking.json")
EMBEDDING_CACHE_FILE = os.path.join(BASE_DIR, "core", "storage", "embedding_cache.json")
FILES_DIRECTORY = os.path.join(BASE_DIR, "core", "files")
CHROMADB_PERSIST_DIRECTORY = os.path.join(BASE_DIR, "core", "storage", "chromadb")
CHROMADB_COLLECTION_NAME = "documents"