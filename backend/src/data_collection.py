import arxiv
import os 
import json
from tqdm import tqdm

DATA_DIR = "data/papers"
META_PATH = "data/metadata.json"

os.makedirs(DATA_DIR, exist_ok=True)

def search_papers(query, max_results=50):
    """
    Search for academic papers on arXiv based on a query.
    Will return a list of arxiv.Result objects.
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )

    client = arxiv.Client()
    results = list(client.results(search))    

    # Filter papers by categories
    allowed_categories = {"stat.ML", "cs.LG", "stat.ME"}
    filtered = [] # initialise filtered list

    for paper in results:
        if any(cat in allowed_categories for cat in paper.categories):
            filtered.append(paper) # add paper to filtered list

    return filtered

def download_paper(paper, save_dir=DATA_DIR):
    """
    Download a paper's PDF and save it to the specified directory.
    Returns the file path of the saved PDF.
    """

    paper_id = paper.entry_id.split('/')[-1] # Extract paper ID from entry_id
    pdf_path = os.path.join(save_dir, f"{paper_id}.pdf")

    # Skip download if file already exists
    if os.path.exists(pdf_path):
        return None
    
    #try-catch block to handle download errors
    try:
        paper.download_pdf(dirpath=save_dir, filename=f"{paper_id}.pdf")
    except Exception as e:
        print(f"Error downloading {paper_id}: {e}")
        return None
    
    #define the metadata to be returned
    metadata = {
        "arxiv_id": paper_id,
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "abstract": paper.summary,
        "published": paper.published.strftime("%Y-%m-%d"),
        "categories": paper.categories,
        "pdf_path": pdf_path
    }

    return metadata

def collect_regression_papers():
    queries = [
        "regression analysis",
        "linear regression",
        "ridge regression lasso",
        "kernel regression",
        "gaussian process regression"]
    
    all_papers = [] # initialise list to hold all paper metadata
    seen_ids = set() # initialise set to track seen paper IDs

    print ("Collecting regression papers from arXiv...")
    for query in queries:
        results = search_papers(query, max_results=50)
        all_papers.extend(results) # accumulate results from each query
    
    metadata_list = [] # initialise list to hold metadata of downloaded papers

    for paper in tqdm(all_papers, desc="Downloading papers"):
        paper_id = paper.entry_id.split('/')[-1]
        if paper_id in seen_ids:
            continue # skip already seen papers
        seen_ids.add(paper_id)

        metadata = download_paper(paper)
        if metadata:
            metadata_list.append(metadata)
    
    # Save metadata to JSON file
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2)
    
    print(f"Saved {len(metadata_list)} papers.")
    print(f"Metadata -> {META_PATH}")
    print(f"PDF -> {DATA_DIR}")

if __name__ == "__main__":
    collect_regression_papers()