import os
import json
from dotenv import load_dotenv
from retrieval import RetrievalSystem
from google import genai

# ---------------- ENV SETUP ----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found in environment variables")

CACHE_FILE = "cache/scholar_cache.json"
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
#       SCHOLAR AI
# =========================
class ScholarAI:
    def __init__(self, top_k=5, max_context_chars=4000, expert_mode=True):
        print("Initialising retrieval system...")
        self.retriever = RetrievalSystem()
        self.top_k = top_k
        self.max_context_chars = max_context_chars
        self.expert_mode = expert_mode
        self.cache = self._load_cache()
        print("ScholarAI ready.\n")

    # ---------------- Cache ----------------
    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")

    # ---------------- Utilities ----------------
    def _deduplicate_chunks(self, chunks):
        seen = set()
        deduped = []
        for chunk in chunks:
            text = chunk["text"].strip()
            if text not in seen:
                deduped.append(chunk)
                seen.add(text)
        return deduped

    def _sort_chunks_by_relevance(self, chunks):
        return sorted(
            chunks,
            key=lambda c: c.get("metadata", {}).get("similarity_score", 0),
            reverse=True
        )

    def _prepare_context(self, chunks):
        chunks = self._deduplicate_chunks(chunks)
        chunks = self._sort_chunks_by_relevance(chunks)

        combined_text = " ".join([c["text"] for c in chunks])

        # With Gemini 2.5 Pro (1M+ token context) we can include full context.
        # Return combined text directly; summarisation/truncation is no longer enforced here.
        return combined_text

    # ---------------- Prompt Builder ----------------
    def _build_prompt(self, query, chunks):
        numbered_context = "\n\n".join(
            [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(chunks)]
        )

        base_prompt = f"""
You are an expert researcher in statistical learning and regression analysis.

CRITICAL INSTRUCTIONS:
1. Answer ONLY using information from the provided papers
2. Include ALL relevant technical terminology (L1, L2, regularization, etc.)
3. Provide mathematical formulations when relevant
4. Cite sources using [1], [2], etc.
5. Be comprehensive but precise

Question: {query}

Research Papers:
{numbered_context}

Provide a thorough answer covering:
- Clear definitions with proper terminology
- Mathematical formulation (if applicable)
- Key properties and characteristics
- Practical implications
- Comparisons (if asked)

Answer:
"""

        return base_prompt

    def _build_structured_prompt(self, query, chunks):
        # Build a prompt that requests a JSON structured response
        numbered_context = "\n\n".join(
            [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(chunks)]
        )

        prompt = f"""
You are an expert researcher in statistical learning and regression analysis.

INSTRUCTIONS: Reply with a JSON object with keys: `answer` (string), `key_concepts` (array of strings), `citations` (array of integers), `confidence` (high|medium|low). Use only the provided context and cite using [1], [2], etc.

Question: {query}

Research Papers:
{numbered_context}

JSON Response:
"""

        return prompt

    # ---------------- Expert Answer ----------------
    def generate_expert_answer(self, query):
        # Return cached answer if exists
        if query in self.cache:
            print("Using cached answer for query.")
            cached = self.cache[query]
            return cached["answer"], cached["chunks"]

        print(f"\nRetrieving top-{self.top_k} chunks for your query...")
        chunks = self.retriever.retrieve(query, k=self.top_k)

        if not chunks:
            return "No relevant papers found for this query.", []

        # Prepare context
        _ = self._prepare_context(chunks)

        # Use the non-structured prompt for now
        prompt = self._build_prompt(query, chunks)

        try:
            # Correct API call for google.genai
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            answer_text = response.text

        except Exception as e:
            print(f"Gemini generation failed: {e}")
            print("Falling back to simple concatenation...")
            answer_text = self.retriever.simple_concat_answer(chunks)

        # Cache result
        self.cache[query] = {
            "answer": answer_text,
            "chunks": chunks
        }
        self._save_cache()

        return answer_text, chunks

    def generate_expert_answer_structured(self, query):
        """Version with structured JSON output"""
        if query in self.cache:
            print("Using cached answer for query.")
            cached = self.cache[query]
            return cached["answer"], cached["chunks"]

        print(f"\nRetrieving top-{self.top_k} chunks for your query...")
        chunks = self.retriever.retrieve(query, k=self.top_k)

        if not chunks:
            return "No relevant papers found for this query.", []

        # Build prompt that requests JSON
        numbered_context = "\n\n".join(
            [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(chunks)]
        )

        prompt = f"""You are an expert researcher in statistical learning and regression analysis.

CRITICAL INSTRUCTIONS:
1. Answer ONLY using information from the provided papers
2. Include ALL relevant technical terminology (L1, L2, regularization, etc.)
3. Provide mathematical formulations when relevant
4. Cite sources using [1], [2], etc.
5. Be comprehensive but precise

Question: {query}

Research Papers:
{numbered_context}

Provide a thorough answer covering:
- Clear definitions with proper terminology
- Mathematical formulation (if applicable)
- Key properties and characteristics
- Practical implications
- Comparisons (if asked)

IMPORTANT: Your response must use proper citation format [1], [2], etc. and include technical terms like "L2 penalty", "regularization", "L1 norm" where relevant.

Answer:"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt
            )
            
            answer_text = response.text

        except Exception as e:
            print(f"Gemini generation failed: {e}")
            answer_text = "Error generating answer."

        # Cache result
        self.cache[query] = {
            "answer": answer_text,
            "chunks": chunks
        }
        self._save_cache()

        return answer_text, chunks


# =========================
#         CLI
# =========================
if __name__ == "__main__":
    scholar_ai = ScholarAI(top_k=5, max_context_chars=4000, expert_mode=True)

    print("\nTip: Ask questions about regression, LASSO, ridge, elastic net, and other ML/stat topics.")
    print("Type 'exit' or 'quit' to leave.\n")

    suggested_questions = [
        "What is ridge regression?",
        "Explain LASSO regression",
        "What is the bias-variance tradeoff?",
        "Compare ridge and LASSO",
        "What is elastic net regression?",
        "Explain regularization methods"
    ]

    print("Suggested questions:")
    for q in suggested_questions:
        print(f"  - {q}")
    print()

    while True:
        query = input("Ask your question: ").strip()

        if query.lower() in ["exit", "quit"]:
            print("Goodbye")
            break

        if not query:
            continue

        print("\nGenerating expert answer... This may take a few seconds.\n")

        answer, chunks = scholar_ai.generate_expert_answer(query)

        print("=" * 80)
        print("Answer:\n")
        print(answer)
        print("=" * 80)

        print("\nSources (sorted by relevance):")
        seen_papers = set()

        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            paper_title = metadata.get("paper_title", "Unknown")
            paper_id = metadata.get("paper_id", "")
            authors = metadata.get("authors", "")
            section = metadata.get("section", "")
            score = metadata.get("similarity_score", None)

            paper_key = (paper_title, paper_id)

            if paper_key not in seen_papers:
                seen_papers.add(paper_key)
                print(f"\n{i}. {paper_title}")

                if authors:
                    print(f"   Authors: {authors}")

                if paper_id:
                    arxiv_id = paper_id.split("v")[0]
                    print(f"   Link: https://arxiv.org/abs/{arxiv_id}")

                if section:
                    print(f"   Section: {section}")

                if score is not None:
                    print(f"   Relevance score: {score:.4f}")
