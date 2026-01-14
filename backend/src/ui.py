import streamlit as st
from typing import List, Optional


def inject_css(*args, **kwargs):
    """No-op: prefer native Streamlit styling."""
    return


def render_header(title: str, subtitle: str, github_url: Optional[str] = None):
    """Render header using native Streamlit components."""
    cols = st.columns([4, 1])
    with cols[0]:
        st.header(title)
        st.caption(subtitle)
    with cols[1]:
        if github_url:
            st.markdown(f"[GitHub]({github_url})")
    st.divider()


def example_chips(examples: List[str]):
    """Render examples as a 3-column grid of buttons.

    Clicking a chip sets `st.session_state['query']` and triggers a rerun.
    """
    cols = st.columns(3)
    for idx, q in enumerate(examples):
        with cols[idx % 3]:
            if st.button(q, key=f"chip-{idx}", use_container_width=True):
                st.session_state['query'] = q
                try:
                    st.experimental_rerun()  # type: ignore[attr-defined]
                except Exception:
                    try:
                        st.rerun()
                    except Exception:
                        pass


def skeleton_card(message: str = "Loading..."):
    """Show a simple placeholder/info message and return the placeholder."""
    placeholder = st.empty()
    placeholder.info(message)
    return placeholder


def render_answer_card(answer: str, preview_limit: int = 800, download_name: str = "answer.txt"):
    """Render generated answer with a short preview and an expander for the full text."""
    st.subheader("Generated Answer")
    preview = answer if len(answer) <= preview_limit else answer[:preview_limit].rsplit("\n", 1)[0] + "\n..."
    st.write(preview)
    with st.expander("Show full answer and download"):
        st.write(answer)
        st.download_button("Download answer (txt)", answer, file_name=download_name)


def render_metadata_card(answer: str, used_chunks: List[dict]):
    """Show basic metadata metrics: word count and number of distinct sources."""
    wc = len(answer.split()) if isinstance(answer, str) else 0
    sources = len(
        {
            (c.get("metadata", {}).get("paper_id") or c.get("metadata", {}).get("paper_title"))
            for c in used_chunks
        }
    )
    st.metric("Word count", wc)
    st.metric("Sources used", sources)