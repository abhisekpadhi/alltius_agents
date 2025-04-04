from flask import Flask
from flask_cors import CORS

from service import rag_service
from datetime import datetime, timezone
from flask import request, jsonify
import os
from flask import send_file

app = Flask(__name__)
CORS(app)

# Register the rag routes
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    collection_name = data.get("collection", "")
    if not collection_name:
        return jsonify({"error": "Missing collection parameter"}), 400
    if not query:
        return jsonify({"error": "Missing query"}), 400
    
    if collection_name == "alltius_rag_chunks_insurance":
        bucket = "Insurance PDFs"
    if collection_name == "alltius_rag_chunks_angelone":
        bucket = "AngelOne"

    # if bucket is empty, return an error
    if bucket == "":
        return jsonify({"error": "Invalid collection"}), 400
            
    return rag_service.handle_chat(query, collection_name, bucket)

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
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }), 200
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
