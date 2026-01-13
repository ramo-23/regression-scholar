# RegressionScholar

RegressionScholar is a Retrieval-Augmented Generation (RAG) prototype for exploring academic research on regression methods. It enables natural language queries over a curated collection of papers (arXiv) and produces answers grounded in the source literature with inline citations.

## Overview

This repository contains an end-to-end RAG pipeline focused on regression analysis topics (ridge regression, LASSO, elastic net and related methods). The main components are:

- Document ingestion and chunking
- Embedding generation and a persistent vector store (ChromaDB)
- Semantic retrieval with optional summarisation
- LLM-based answer generation with citation grounding
- An evaluation suite for retrieval and generation quality

## Features

- Semantic search: retrieve relevant paper sections using dense embeddings
- LLM generation: generate grounded answers using Google Gemini 2.5 Flash
- Inline citations: answers reference source papers using numbered citations
- Caching: query results are cached to speed up repeated evaluations
- Evaluation framework: retrieval (recall, precision, MRR) and generation (concept coverage, citation rate)

## Tech stack

- Embeddings: `sentence-transformers/all-mpnet-base-v2`
- Vector store: ChromaDB (persistent client)
- LLM: Google Gemini 2.5 Flash
- Summarisation (optional): Hugging Face summarisation pipeline
- Data source: arXiv papers (PDFs → processed text chunks)

Note: Gemini 2.5 Flash provides an expanded context window compared with much smaller models; if you require a 1M+ token context, consider adapting `src/generation.py` for a Pro-tier model.

## Results

### Retrieval performance
| Metric | k=3 | k=5 | k=10 |
|--------|-----|-----|------|
| Recall | 24.4% | 36.9% | 45.7% |
| Precision | 26.7% | 22.7% | 17.3% |
| MRR | 0.500 | 0.547 | 0.565 |

### Generation quality
- Concept coverage: 50%
- Citation rate: 80%
- Average answer length: 621 words

## Example query

**Query**: "Compare ridge and LASSO"

**Answer (excerpt)**: Ridge regression is a regularised linear regression method that adds an L2 penalty term (λ||β||₂²) to the loss function. This shrinkage technique helps prevent overfitting by constraining coefficient magnitudes; LASSO uses an L1 penalty and promotes sparsity in the coefficients.

## Project layout

```
regression-scholar/
├── data/
│   ├── papers/          # downloaded PDFs
│   ├── processed/       # text chunks and processed output
│   └── metadata.json    # paper metadata
├── src/
│   ├── data_collection.py
│   ├── processing.py
│   ├── embedding.py
│   ├── retrieval.py
│   ├── generation.py
│   └── evaluation.py
├── notebooks/
│   └── analysis.ipynb
├── cache/
│   └── scholar_cache.json
├── test_questions_mapped.json
└── README.md
```

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/ramo-23/regression-scholar
cd regression-scholar
pip install -r requirements.txt
```

Add your Gemini API key to a `.env` file in the project root:

```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

## Usage

Interactive generation (CLI):

```bash
python src/generation.py
```

Run the evaluation suite (loads `test_questions_mapped.json`):

```bash
python src/evaluation.py
```

To force regeneration of answers, remove the cache file:

```bash
rm -rf cache/scholar_cache.json
```

## Evaluation

The evaluation suite measures retrieval (recall@k, precision@k, MRR) and basic generation metrics (concept coverage, citation rate, answer length). Test questions are loaded from `test_questions_mapped.json`, which maps questions to relevant papers as ground truth.

## Limitations and future work

Current limitations:

1. Retrieval recall has room for improvement; consider hybrid retrieval and reranking
2. Concept coverage may be improved through prompt iterations and evaluation refinements
3. Large-context handling is dependent on the LLM tier used (Flash vs Pro)

Potential improvements:

1. Add cross-encoder reranking or a re-ranking stage
2. Fine-tune or adapt embeddings for the regression domain
3. Improve prompt engineering and enforce structured outputs for automated evaluation
4. Add CI tests for reproducible evaluation runs

## Contributing

Contributions, issues and feature requests are welcome. Please open an issue or submit a pull request.

## License

MIT