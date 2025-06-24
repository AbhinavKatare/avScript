# ✅ NEW (correct)
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

def get_pdf_context(query):
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        db = FAISS.load_local("faiss_index", model)
        docs = db.similarity_search(query, k=2)
        return "\n".join([d.page_content for d in docs])
    except:
        return ""
