import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import chromadb
import os

CHUNKS_PATH = "data/processed/paper_chunks.json"
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "regression_papers"

def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks")
    return chunks

def create_embeddings(chunks, model_name="all-mpnet-base-v2", batch_size=64):
    print("Loading embedding model...")
    model = SentenceTransformer(model_name)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = [] # Store embeddings here

    print("Creating embeddings...")
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        embeddings.extend(batch_embeddings)
    return embeddings

def store_embeddings(chunks, embeddings):
    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection if it exists
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    print("Storing embeddings in ChromaDB...")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "paper_id": chunk["paper_id"],
            "paper_title": chunk["paper_title"],
            "authors": ", ".join(chunk["authors"]),
            "section": chunk["section"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print("✅ Embeddings stored and persisted to disk.")


def build_vector_store():
    chunks = load_chunks()
    embeddings = create_embeddings(chunks)
    store_embeddings(chunks, embeddings)

if __name__ == "__main__":
    build_vector_store()