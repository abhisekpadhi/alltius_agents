from dotenv import load_dotenv
from qdrant_client import QdrantClient
import voyageai
from qdrant_client.models import VectorParams, Distance
from lib.logging import log
import openai
import os

# Load variables from .env file
load_dotenv()

# Access your keys
config = {
    "openai_api_key": os.getenv("OPENAI_AZURE_API_KEY"),
    "openai_api_version": os.getenv("OPENAI_AZURE_API_VERSION"),
    "openai_azure_deployment": os.getenv("OPENAI_AZURE_DEPLOYMENT"),
    "openai_azure_endpoint": os.getenv("OPENAI_AZURE_ENDPOINT"),
    "voyage_api_key": os.getenv("VOYAGE_API_KEY"),
    "qdrant_url": os.getenv("QDRANT_URL"),
    "qdrant_api_key": os.getenv("QDRANT_API_KEY")
}

print(config)

COLLECTION_NAME_INSURANCE = "alltius_rag_chunks_insurance"
COLLECTION_NAME_ANGELONE = "alltius_rag_chunks_angelone"
VOYAGE_MODEL = "voyage-3"

# Initialize once
qdrant = QdrantClient(
    url=config["qdrant_url"], 
    api_key=config["qdrant_api_key"],
)

# Create collection if it doesn't exist
collections = qdrant.get_collections().collections

voyage = voyageai.Client(api_key=config["voyage_api_key"])  # Or use env var

openai = openai.AzureOpenAI(
  api_key = config["openai_api_key"],
  api_version = config["openai_api_version"],
  azure_endpoint = config["openai_azure_endpoint"],
  azure_deployment= config["openai_azure_deployment"]
)

# create collection if it doesn't exist
print("collections", collections)
