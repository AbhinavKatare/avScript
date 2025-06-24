import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer
import os

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return " ".join([page.get_text() for page in doc])

def load_all_pdfs(folder):
    all_docs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            text = extract_text(os.path.join(folder, file))
            all_docs.append(Document(page_content=text))
    return all_docs

def create_vectorstore():
    raw_docs = load_all_pdfs("../data/")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    faiss_index = FAISS.from_documents(chunks, model)
    faiss_index.save_local("faiss_index")

if __name__ == "__main__":
    create_vectorstore()
