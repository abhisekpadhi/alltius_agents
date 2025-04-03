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
