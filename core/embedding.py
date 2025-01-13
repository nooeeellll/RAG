import os
import torch
from transformers import AutoModel, AutoTokenizer
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

class EmbeddingManager:
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = self.pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        self.batch_size = 32

    def embed_text(self, text: str):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    def upload_to_pinecone(self, vectors, namespace="ns1"):
        self.index.upsert(vectors=vectors, namespace=namespace)

    def process_pdfs_and_upload(self, pdf_files, extract_text_func, split_text_func, namespace="ns1"):
        chunks_per_file = {}
        
        for pdf_file in pdf_files:
            text = extract_text_func(pdf_file)
            document_chunks = split_text_func(text)
            vectors_to_upsert = []
            
            # Get filename without extension for the ID
            filename = os.path.splitext(pdf_file.name)[0]
            # Replace spaces and special characters for safe IDs
            safe_filename = filename.replace(' ', '-').replace('/', '_').replace('\\', '_')
            
            for batch_index in range(0, len(document_chunks), self.batch_size):
                batch = document_chunks[batch_index:batch_index + self.batch_size]
                for chunk_index, chunk in enumerate(batch):
                    embedding = self.embed_text(chunk).squeeze().tolist()
                    vector = {
                        "id": f"{safe_filename}-chunk-{batch_index + chunk_index}",
                        "values": embedding,
                        "metadata": {
                            "chunk": chunk,
                            "file_name": pdf_file.name,
                            "chunk_index": batch_index + chunk_index
                        }
                    }
                    vectors_to_upsert.append(vector)
                self.upload_to_pinecone(vectors_to_upsert, namespace)
                vectors_to_upsert.clear()
            
            chunks_per_file[pdf_file.name] = len(document_chunks)
        
        return chunks_per_file