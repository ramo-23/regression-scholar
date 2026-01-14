from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from transformers import pipeline
from pathlib import Path

# Resolve paths relative to backend root so scripts work regardless of cwd
BACKEND_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = str(BACKEND_ROOT / "data" / "chroma")
COLLECTION_NAME = "regression_papers"

class RetrievalSystem:
    def __init__(self, model_name="all-mpnet-base-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)

        print("Setting up ChromaDB client...")
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

        print("Setting up summarizer...")
        # Use a smaller, more reliable model
        self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

        print("Retrieval system initialised.")

    def retrieve(self, query, k=5):
        """
        Embed the query and retrieve top-k similar documents from the collection.
        """
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=k)

        retrieved_chunks = [
            {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "id": results["ids"][0][i]
            }
            for i in range(len(results["documents"][0]))
        ]
        return retrieved_chunks

    def summarize_chunks(self, chunks, max_length=150):
        """
        Summarize multiple chunks into a concise answer.
        Uses proper truncation to avoid index errors.
        """
        combined_text = " ".join([chunk["text"] for chunk in chunks])
        
        # Truncate by character count (rough estimate: 1 token ≈ 4 chars)
        max_chars = 1024 * 4  # ~1024 tokens worth of characters
        if len(combined_text) > max_chars:
            print(f"Warning: Input too long ({len(combined_text)} chars). Truncating to {max_chars} chars.")
            combined_text = combined_text[:max_chars]
        
        try:
            # Let the pipeline handle tokenization with max_length
            summary = self.summarizer(
                combined_text,
                max_length=max_length,
                min_length=30,
                do_sample=False,
                truncation=True,
                clean_up_tokenization_spaces=True
            )
            return summary[0]["summary_text"]
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: return first chunk only
            return chunks[0]["text"][:500] + "..."
    
    def simple_concat_answer(self, chunks, max_chars=800):
        """
        Simple fallback: Just concatenate the most relevant chunks.
        No summarization, just direct text.
        """
        texts = []
        total_chars = 0
        
        for chunk in chunks:
            text = chunk["text"]
            if total_chars + len(text) > max_chars:
                remaining = max_chars - total_chars
                texts.append(text[:remaining] + "...")
                break
            texts.append(text)
            total_chars += len(text)
        
        return " ".join(texts)
    
    def get_answer(self, query, method="simple"):
        """
        Main method to get an answer.
        
        Args:
            query: User's question
            method: "simple" (concatenation) or "summarize" (with model)
        """
        chunks = self.retrieve(query, k=3)  # Reduced to 3 for safety
        
        if method == "simple":
            return self.simple_concat_answer(chunks)
        else:
            try:
                return self.summarize_chunks(chunks)
            except Exception as e:
                print(f"Summarization failed: {e}")
                print("Falling back to simple concatenation...")
                return self.simple_concat_answer(chunks)

# Quick test runner
if __name__ == "__main__":
    retriever = RetrievalSystem()

    print("\nTip: For best results, this system uses simple text concatenation by default.")
    print("The retrieved text is directly from your academic papers.")
    print("\nSuggested questions:")
    print("  - What is ridge regression?")
    print("  - Explain LASSO regression")
    print("  - What is the bias-variance tradeoff?")
    print("  - Compare ridge and LASSO")
    print("  - What is elastic net regression?")
    print("  - Explain regularization methods\n")

    while True:
        query = input("\nAsk about regression (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        print("\nSearching and generating answer...")
        
        # Use simple method by default (more reliable)
        answer = retriever.get_answer(query, method="simple")

        print("\n" + "="*80)
        print("Answer:")
        print(answer)
        print("="*80)
        
        # Show metadata with links
        chunks = retriever.retrieve(query, k=3)
        print("\nSources:")
        seen_papers = set()
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            paper_title = metadata.get('paper_title', 'Unknown')
            paper_id = metadata.get('paper_id', '')
            authors = metadata.get('authors', '')
            section = metadata.get('section', '')
            
            # Create unique identifier to avoid duplicate papers
            paper_key = (paper_title, paper_id)
            source_num = len(seen_papers) + 1 if paper_key not in seen_papers else list(seen_papers).index(paper_key) + 1
            
            if paper_key not in seen_papers:
                seen_papers.add(paper_key)
                print(f"\n{source_num}. {paper_title}")
                if authors:
                    print(f"   Authors: {authors}")
                if paper_id:
                    # Extract arxiv ID without version
                    arxiv_id = paper_id.split('v')[0]
                    print(f"   Link: https://arxiv.org/abs/{arxiv_id}")
                if section:
                    print(f"   Section: {section}")