import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.json"

class VectorStore:
    def __init__(self):
        # 1. Initialize the sentence-transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # 2. Set the embedding dimension for 'all-MiniLM-L6-v2'
        self.dimension = 384
        
        if os.path.exists(INDEX_FILE):
            self.load_store()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = []

    def save_store(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(CHUNKS_FILE, "w") as f:
            json.dump(self.chunks, f)

    def load_store(self):
        self.index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "r") as f:
            self.chunks = json.load(f)

    def embed(self, text):
        # 3. Use the local model to create the embedding
        embedding = self.model.encode(text)
        return np.array(embedding).astype("float32")

    def add_text(self, text):

        # Use a text splitter to create smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=30,
            length_function=len,
        )
        
        # Split the text and process each chunk
        split_chunks = text_splitter.split_text(text)
        
        for chunk in split_chunks:
            if len(chunk.strip()) < 10:
                continue

            emb = self.embed(chunk)
            self.index.add(np.array([emb]))
            self.chunks.append(chunk)
        
        self.save_store()
        print(f"Successfully added {self.index.ntotal} vectors to the index.")

    def search(self, query):
        q_emb = self.embed(query)
        # Reshape the query embedding to (1, dimension)
        q_emb = np.array([q_emb])
        
        # Check if the index is trained and has vectors
        if self.index.ntotal == 0:
            return "The document has not been uploaded or processed yet. Please upload a PDF first."
            
        # Retrieve 3 chunks now that they are smaller
        D, I = self.index.search(q_emb, k=min(self.index.ntotal, 3))
        
        results = [self.chunks[i] for i in I[0] if i < len(self.chunks)]
        return "\n\n".join(results)
