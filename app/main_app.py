import streamlit as st
from pathlib import Path
import json
from retrieval import RetrievalSystem
from generation import ScholarAI

# Basic Streamlit main interface for RegressionScholar

st.set_page_config(page_title="RegressionScholar", layout="wide")

st.title("RegressionScholar")
st.subheader("Ask questions about regression techniques")
st.markdown("A demo interface for semantic retrieval and LLM-powered, citation-grounded answers.")

# Sidebar controls
st.sidebar.header("Configuration")
k = st.sidebar.slider("Number of papers to retrieve (k)", 3, 10, 5)
show_details = st.sidebar.checkbox("Show retrieval details", value=True)
show_full_chunks = st.sidebar.checkbox("Show full chunks", value=False)

# Example questions
EXAMPLES = [
    "What is ridge regression?",
    "Compare ridge and LASSO",
    "Explain LASSO regularisation",
    "When should I use elastic net?",
    "What is the bias-variance tradeoff?"
]

st.sidebar.markdown("**Example questions**")
for q in EXAMPLES:
    if st.sidebar.button(q, key=q):
        st.session_state['query'] = q

# Dataset stats
cache_file = Path('cache/scholar_cache.json')
metadata_file = Path('data/metadata.json')

with st.sidebar.expander('Dataset & cache'):
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            st.write(f"Total papers: {len(metadata)}")
        except Exception:
            st.write("Metadata: could not load file")
    else:
        st.write("Metadata not found")

    if cache_file.exists():
        st.write(f"Cache file size: {cache_file.stat().st_size / 1024:.1f} KB")
    else:
        st.write("Cache not found")

# Main query input
query = st.text_input("Ask your question about regression...", value=st.session_state.get('query', ''))
if st.button("Submit") or query:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        # Initialize systems (lazy)
        with st.spinner('Initializing retrieval and generation...'):
            retriever = RetrievalSystem()
            scholar = ScholarAI(top_k=k)

        with st.spinner('Retrieving relevant chunks...'):
            chunks = retriever.retrieve(query, k=k)

        if not chunks:
            st.info('No relevant papers found for this query.')
        else:
            if show_details:
                st.markdown('**Top retrieved papers (summary):**')
                for i, chunk in enumerate(chunks, 1):
                    md = chunk.get('metadata', {})
                    title = md.get('paper_title', 'Unknown')
                    authors = md.get('authors', '')
                    score = md.get('similarity_score', None)
                    st.write(f"{i}. **{title}**")
                    if authors:
                        st.write(f"   Authors: {authors}")
                    if score is not None:
                        st.write(f"   Relevance score: {score:.4f}")

            if show_full_chunks:
                st.markdown('**Full retrieved chunks:**')
                for i, chunk in enumerate(chunks, 1):
                    st.code(chunk.get('text',''), language='text')

            # Generate answer
            with st.spinner('Generating expert answer...'):
                answer, used_chunks = scholar.generate_expert_answer(query)

            st.markdown('---')
            st.subheader('Generated Answer')
            st.markdown(answer)

            # Sources panel
            with st.expander('Sources (sorted by relevance)'):
                seen = set()
                for i, chunk in enumerate(used_chunks, 1):
                    md = chunk.get('metadata', {})
                    title = md.get('paper_title', 'Unknown')
                    paper_id = md.get('paper_id', '')
                    authors = md.get('authors', '')
                    section = md.get('section', '')
                    score = md.get('similarity_score', None)

                    key = (title, paper_id)
                    if key in seen:
                        continue
                    seen.add(key)

                    st.markdown(f"**{title}**")
                    if authors:
                        st.write(f"Authors: {authors}")
                    if paper_id:
                        arxiv_id = paper_id.split('v')[0]
                        st.write(f"Link: https://arxiv.org/abs/{arxiv_id}")
                    if section:
                        st.write(f"Section: {section}")
                    if score is not None:
                        st.write(f"Relevance score: {score:.4f}")

            # Download answer as text
            st.download_button('Download answer (txt)', answer, file_name='answer.txt')

# Footer
st.markdown('---')
st.markdown('[Repo on GitHub](https://github.com/ramo-23/regression-scholar)')
