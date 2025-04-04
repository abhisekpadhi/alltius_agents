# Alltius RAG agent

- This is a RAG agent that can answer user queries from support documentations.
- Currently it's indexed with
  - Insurance: insurance policy documents from pdf files &
  - Stock broker: support documents from URL

## Features

- It has 2 different collections for data isolation by vendor.
- It support pdf ingestion & web url ingestion.

## Tech stack

- Backend: Python, Flask
- VectorDB: Qdrant
- Retrival: VoyageAI
- Frontend: NextJS

## How to run

### Config

- OpenAI API key
- VoyageAI API Key
- Qdrant API Key

### Backend

- Setup dev environment

```shell
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

- Install requirements

```shell
pip install -r requirements.txt
```

- Run app (flask server)

```shell
python3 app.py
```

### Frontend

- Setup dev environment

```shell
cd frontend
```

- Install requirements

```shell
npm install
```

- Run app (flask server)

```shell
npm run dev
```

## API's

- Chat API

**Request**

```shell
curl --location 'http://localhost:5050/api/v1/rag/chat' \
--header 'Content-Type: application/json' \
--data '{
    "query": "Is there a limit on the amount of funds that I can add to my Angel One account?",
    "collection": "alltius_rag_chunks_angelone"
}'
```

**Response - success**

```json
{
  "answer": "Yes, there is a limit on the amount of funds that you can add to your Angel One account. The limit for fund addition via UPI is 1 lakh per day. For net banking, the limit will be applicable as per the bank account.",
  "sources": [
    "https://www.angelone.in/support/add-and-withdraw-funds/add-funds"
  ]
}
```

- Health API

```shell
curl --location 'http://localhost:5050/api/v1/rag/health'
```

**Response - success**
```json
{
  "status": "healthy",
  "timestamp": "2025-04-04T04:22:17.116120+00:00Z"
}
```

- Error response - common to all API's
```json
{
  "error": 
  "Invalid collection"
}
```

## Optimisations

### Reduce hallucinations

#### Also check semantic distance / relevance score

- We can access the distance score from Qdrant and set a cutoff:

```python
hits = qdrant.search(
    collection_name=COLLECTION_NAME,
    query_vector=vector,
    limit=top_k,
    with_payload=True,
    with_vectors=False
)

# Check score threshold
if all(h.score < 0.6 for h in hits):  # adjust threshold
    return None, None
```

### Security - Access control

- We can pass `AccessContext` from the API routes down to the service layer
- `AccessContext`: `{user_id, tenant_id, collection_id}`
- There will be an access control layer that decides given an `AccessContext` and `sources`, it it allowed or not
