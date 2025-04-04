from config import qdrant, voyage, VOYAGE_MODEL, TOP_K, MIN_RESULTS
from qdrant_client import QdrantClient
import voyageai

class Repository:
    def __init__(self, 
                 qdrant: QdrantClient, 
                 voyage: voyageai.Client, 
                 voyage_model: str, 
                 top_k: int = TOP_K, 
                 min_results: int = MIN_RESULTS):
        self.qdrant = qdrant
        self.voyage = voyage
        self.voyage_model = voyage_model
        self.top_k = top_k
        self.min_results = min_results

    def search_chunks(self, query, collection_name):
        vector = self.voyage.embed([query], model=self.voyage_model).embeddings[0]
        hits = self.qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=self.top_k
        )
        chunks = [h.payload['text'] for h in hits]
        sources = list({h.payload.get("source", "unknown") for h in hits})

        if len(chunks) < self.min_results:
            return None, None  # not enough context
        
        return chunks, sources

repository = Repository(qdrant, voyage, VOYAGE_MODEL)
