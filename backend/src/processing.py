import fitz # PyMuPDF
import os 
import json
import re
from tqdm import tqdm

PAPERS_DIR = "data/papers"
META_PATH = "data/metadata.json"
OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SECTION_HEADERS = [
    "abstract", "introduction", "background", "related work",
    "method", "methods", "methodology", "approach",
    "model", "models", "algorithm",
    "experiments", "experimental setup", "results", "evaluation",
    "discussion", "conclusion", "conclusions"]

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s", " ", text)
    return text.strip() # Remove leading/trailing whitespace

def extract_text_from_pdf(pdf_path):
    """
    This function extracts text from a PDF page by page.
    """

    doc = fitz.open(pdf_path)
    pages = [] # initialise pages list

    for page in doc:
        text = page.get_text("text")
        if text:
            pages.append(text)
    
    full_text = "\n".join(pages)
    return full_text

def split_into_sections(text):
    """
    We will try to split the text into sections based on common section headers.    
    """

    sections = {} # initialise sections dictionary
    current_section = "unknown"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines: 
        line_clean = line.strip().lower()

        # Detect section headers
        if any(line_clean.startswith(h) for h in SECTION_HEADERS) and len(line_clean) < 50:
            current_section = line_clean
            sections[current_section] = []
        else:
            sections[current_section].append(line)

    # Join lines back into text for each section
    for key in sections:
        sections[key] = " ".join(sections[key])

    return sections

def chunk_text(text, min_tokens = 300, max_tokens = 800):
    """
    Chunk text into smaller pieces based on token limits.
    Here we use a simple whitespace tokenizer for demonstration.
    """

    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    
    # Add any remaining words as a final chunk
    if len(current_chunk) >= min_tokens:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_all_papers():
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)
    
    all_chunks = [] # initialise list to hold all chunks

    for paper in tqdm(metadata_list, desc = "Processing papers"):
        pdf_path = paper["pdf_path"]

        if not os.path.exists(pdf_path):
            continue # skip if PDF does not exist

        # try-catch block to handle processing errors
        try:
            raw_text = extract_text_from_pdf(pdf_path)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            continue

        sections = split_into_sections(raw_text)

        chunk_index = 0

        for section, text in sections.items():
            section_text = clean_text(text)

            # Skip useless sections
            if section in ["references", "acknowledgements", "acknowledgments"]:
                continue

            chunks = chunk_text(section_text)

            for chunk in chunks:
                chunk_data = {
                    "text": chunk,
                    "paper_id": paper["arxiv_id"],
                    "paper_title": paper["title"],
                    "authors": paper["authors"],
                    "section": section,
                    "chunk_index": chunk_index
                }

                all_chunks.append(chunk_data)
                chunk_index += 1

    # Save all chunks to JSON file
    chunks_path = os.path.join(OUTPUT_DIR, "paper_chunks.json")

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"Saved {len(all_chunks)} chunks.")

if __name__ == "__main__":
    process_all_papers()
