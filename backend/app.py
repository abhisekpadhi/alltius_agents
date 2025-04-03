from flask import Flask, request, jsonify
from config import qdrant, voyage, VOYAGE_MODEL, openai
from datetime import datetime, timezone
import json
from lib.logging import log
from flask import send_file
import os
import urllib.parse
from recall import recall
from flask_cors import CORS

LOG_FILE = "chat_history.log"

app = Flask(__name__)
CORS(app)

TOP_K = 3    
MIN_RESULTS = 1

def search_chunks(query, collection_name, min_results):
    vector = voyage.embed([query], model=VOYAGE_MODEL).embeddings[0]
    hits = qdrant.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=TOP_K
    )
    chunks = [h.payload['text'] for h in hits]
    sources = list({h.payload.get("source", "unknown") for h in hits})

    if len(chunks) < min_results:
        return None, None  # not enough context
    
    return chunks, sources

def generate_answer(context_chunks, question):
    context = "\n\n".join(context_chunks)
    prompt = f"""You are an assistant helping answer questions from documents.

Context:
{context}

Question: {question}
Answer:"""
    
    log.info("prompt", {
        "prompt": prompt
    })

    response = openai.chat.completions.create(
        model="GPT4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
        top_p=0.95,
    )
    return response.choices[0].message.content

def log_chat_to_file(user_id, query, response):
    log_entry = {
        "user_id": user_id,
        "query": query,
        "response": response,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, indent=2) + "\n\n")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    collection_name = data.get("collection", "")
    if not collection_name:
        return jsonify({"error": "Missing collection parameter"}), 400
    if not query:
        return jsonify({"error": "Missing query"}), 400
    
    # Cache the query and response
    cache_key = f"{collection_name}:{query}"

    cached_response = recall.recall(cache_key)
    if cached_response:
        return jsonify(cached_response)

    log.info("cache_miss", {
        "cache_key": cache_key
    })

    context_chunks, sources = search_chunks(query, collection_name, MIN_RESULTS)
    
    # Dont return an answer if there is no context
    if not context_chunks:
        return jsonify({
            "answer": "I don't know",
            "sources": []
        })
    
    answer = generate_answer(context_chunks, query)

    log_chat_to_file(query, context_chunks, answer)

    bucket = ""

    if collection_name == "alltius_rag_chunks_insurance":
        bucket = "Insurance PDFs"
    if collection_name == "alltius_rag_chunks_angelone":
        bucket = "AngelOne"

    if bucket == "":
        return jsonify({"error": "Invalid collection"}), 400
    
    sources_cleaned = []

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

@app.route("/file/<path:file_name>")
def get_file(file_name):
    bucket = request.args.get('bucket', '')
    if not bucket:
        return jsonify({"error": "Missing bucket parameter"}), 400

    file_path = os.path.join("/Users/abhisekp/personal/interviews/alltius/resources", bucket, file_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        return send_file(
            file_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=file_name
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
