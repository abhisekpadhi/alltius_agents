import requests
import uuid
from bs4 import BeautifulSoup
from config import qdrant, voyage, VOYAGE_MODEL, COLLECTION_NAME_ANGELONE
from lib.logging import log

def extract_text_from_url(url):
    log.info("Fetching: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text

def chunk_text(text, max_words=500):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def ingest_webpage(url, collection_name):
    raw_text = extract_text_from_url(url)
    chunks = chunk_text(raw_text)

    vectors = voyage.embed(chunks, model=VOYAGE_MODEL).embeddings
    payloads = [{"text": c, "source": url} for c in chunks]
    ids = [str(uuid.uuid4()) for _ in chunks]

    qdrant.upsert(
        collection_name=collection_name,
        points=[{
            "id": ids[i],
            "vector": vectors[i],
            "payload": payloads[i]
        } for i in range(len(chunks))]
    )
    log.info("Uploaded chunks to Qdrant", {
        "num_chunks": len(chunks),
        "url": url,
        "collection_name": collection_name
    })

if __name__ == "__main__":
    skip_urls = [
        "https://www.angelone.in/support/add-and-withdraw-funds/add-funds"
    ]
    with open("../resources/angelone/urls.txt", "r") as f:
        for line in f:
            if line.strip() in skip_urls:
                continue
            # ingest_webpage(
            #     line.strip(),
            #     COLLECTION_NAME_ANGELONE
            # )