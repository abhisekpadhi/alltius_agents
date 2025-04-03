from config import qdrant, COLLECTION_NAME_INSURANCE, COLLECTION_NAME_ANGELONE, VectorParams, Distance
from lib.logging import log

if not qdrant.collection_exists(COLLECTION_NAME_INSURANCE):
    log.info("Collection does not exist, creating collection", {
        "collection_name": COLLECTION_NAME_INSURANCE,
        "action": "create_collection"
    })
    qdrant.create_collection(
        collection_name=COLLECTION_NAME_INSURANCE,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
    log.info("Created collection", {
        "collection_name": COLLECTION_NAME_INSURANCE,
        "action": "create_collection"
    })

if not qdrant.collection_exists(COLLECTION_NAME_ANGELONE):
    log.info("Collection does not exist, creating collection", {
        "collection_name": COLLECTION_NAME_ANGELONE,
        "action": "create_collection"
    })
    qdrant.create_collection(
        collection_name=COLLECTION_NAME_ANGELONE,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
    log.info("Created collection", {
        "collection_name": COLLECTION_NAME_ANGELONE,
        "action": "create_collection"
    })



