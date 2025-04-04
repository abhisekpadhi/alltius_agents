import pdfplumber
import uuid
from config import qdrant, voyage, COLLECTION_NAME_INSURANCE, VOYAGE_MODEL
from qdrant_client.models import VectorParams, Distance
import os
from lib.logging import log

def extract_chunks(pdf_path, max_chunk_words=500):
    """
    Extracts text and (if present) tables from each PDF page.
    Returns a list of clean text chunks.
    """
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 1. Extract plain text
            if page_text := page.extract_text():
                chunks.extend(chunk_text(page_text.strip(), max_chunk_words))

            # 2. Extract tables if any
            tables = page.extract_tables()
            for table in tables or []:
                if table:
                    # Handle None values in table cells by converting them to empty strings
                    table_str = "\n".join([
                        "\t".join(str(cell) if cell is not None else "" for cell in row)
                        for row in table if row
                    ])
                    chunks.extend(chunk_text(table_str.strip(), max_chunk_words))
    return chunks

def chunk_text(text, max_words=500):
    """
    Splits a long string into smaller chunks with a word limit.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def ingest_pdf(pdf_path, collection_name):
    file_name = os.path.basename(pdf_path)
    print(f"Processing: {file_name}")
    chunks = extract_chunks(pdf_path)

    if not chunks:
        log.info("No text found in {file_name}. Skipping upload.", {
            "file_name": file_name,
            "action": "skip_upload"
        })
        return

    vectors = voyage.embed(chunks, model=VOYAGE_MODEL).embeddings
    payloads = [{"text": c, "source": file_name} for c in chunks]
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
        "file_name": file_name,
        "action": "upload_chunks"
    })

if __name__ == "__main__":
    files = [
        # "/Users/abhisekp/personal/interviews/alltius/resources/Insurance PDFs/America's_Choice_2500_Gold_SOB (1) (1).pdf", 
        "/Users/abhisekp/personal/interviews/alltius/resources/Insurance PDFs/America's_Choice_5000_Bronze_SOB (2).pdf",
        # "/Users/abhisekp/personal/interviews/alltius/resources/Insurance PDFs/America's_Choice_5000_HSA_SOB (2).pdf",
        # "/Users/abhisekp/personal/interviews/alltius/resources/Insurance PDFs/America's_Choice_7350_Copper_SOB (1) (1).pdf",
        # "/Users/abhisekp/personal/interviews/alltius/resources/Insurance PDFs/America's_Choice_Medical_Questions_-_Modified_(3) (1).pdf"
    ]
    # for file in files:
    #     ingest_pdf(
    #         file, 
    #         COLLECTION_NAME_INSURANCE
    #     ) 
