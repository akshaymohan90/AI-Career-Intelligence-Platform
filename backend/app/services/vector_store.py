import chromadb


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="career_knowledge"
)


def add_document(
    document_id: str,
    text: str,
    metadata: dict | None = None
):
    collection.upsert(
        ids=[document_id],
        documents=[text],
        metadatas=[metadata or {}]
    )


def search_documents(
    query: str,
    n_results: int = 3
):
    return collection.query(
        query_texts=[query],
        n_results=n_results
    )
