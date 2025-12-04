from app.services.vectorstore.pinecoin_client import get_index
from sentence_transformers import SentenceTransformer
import torch

BASE_PMC_URL = "https://pmc.ncbi.nlm.nih.gov/articles/"

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO', device=device)
index = get_index()

def semantic_search(query, top_k=2):
    index = get_index()
    # Step 1: Embed the user query
    query_vector = model.encode(query, convert_to_numpy=True, show_progress_bar=False)

    # Step 2: Query Pinecone
    results = index.query(
        vector=query_vector.tolist(),
        top_k=top_k,
        include_metadata=True
    )

    # Step 3: Display results

    evidences = []
    for match in results.matches:
        meta = match.metadata.copy() if match.metadata else {}
        meta["pmid"] = meta.get("pmid")
        meta["score"] = match.score
        meta["pmcid"] = meta.get("pmcid")  # store vector id too
        meta["link"] = f"{BASE_PMC_URL}{meta.get('pmcid', '').split('_')[0]}"
        meta["article_title"] = meta.get("article_title", "No Title")
        meta["pub_year"] = meta.get("pub_year", "")
        meta["article_type"] = meta.get("article_type", "")
        evidences.append(meta)
        
    return evidences
