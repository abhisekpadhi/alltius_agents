from config import openai, OUT_OF_CONTEXT_RESPONSE, TOP_K, MIN_RESULTS, LOG_FILE
from datetime import datetime, timezone
import json
from flask import jsonify
from recall import recall
from lib.logging import log
import urllib.parse
from repository import repository, Repository
from openai import AzureOpenAI

class RAGService:
    def __init__(self, 
                 repository: Repository, 
                 openai: AzureOpenAI, 
                 out_of_context_response: str):
        self.openai = openai
        self.out_of_context_response = out_of_context_response
        self.repository = repository

    def search_chunks(self, query, collection_name):
        return self.repository.search_chunks(query, collection_name)

    def generate_answer(self, context_chunks, question):
        context = "\n\n".join(context_chunks)
        prompt = f"""You are an assistant helping answer questions from documents.
- If no relevant information exists, respond with exactly: {self.out_of_context_response}
- Response should be direct and fact-based
- Use short, clear sentences
- Focus exclusively on the asked question

Context:
{context}

Question: {question}
Answer:"""

        response = self.openai.chat.completions.create(
            model="GPT4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
            top_p=0.95,
        )
        return response.choices[0].message.content
    
    def log_chat_to_file(self, query, context_chunks, answer):
        log_entry = {
            "query": query,
            "context_chunks": context_chunks,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, indent=2) + "\n\n")

    def handle_chat(self, query, collection_name, bucket):    
        # Cache the query and response
        cache_key = f"{collection_name}:{query}"

        cached_response = recall.recall(cache_key)
        if cached_response:
            return jsonify(cached_response)

        log.info("cache_miss", {
            "cache_key": cache_key
        })

        context_chunks, sources = self.search_chunks(query, collection_name)
        
        # Dont return an answer if there is no context
        if not context_chunks:
            return jsonify({
                "answer": "I don't know",
                "sources": []
            })
        
        answer = self.generate_answer(context_chunks, query)
        
        self.log_chat_to_file(query, context_chunks, answer)

        sources_cleaned = []

        # If answer contains "I don't know", return empty sources
        if OUT_OF_CONTEXT_RESPONSE in answer:
            sources_cleaned = []
        else:
            if collection_name == "alltius_rag_chunks_insurance":
                sources_cleaned = [
                    f"/file/{urllib.parse.quote(source)}?bucket={urllib.parse.quote(bucket)}"
                    for source in sources
                ]
            if collection_name == "alltius_rag_chunks_angelone":
                sources_cleaned = sources

        result = {
            "answer": answer,
            "sources": sources_cleaned
        }

        # Cache the answer
        recall.remember(cache_key, result)

        return jsonify(result)

rag_service = RAGService(
    repository=repository,
    openai=openai,
    out_of_context_response=OUT_OF_CONTEXT_RESPONSE
)