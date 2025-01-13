import os
import torch
from pinecone import Pinecone
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone and other components
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
model_name = os.getenv('MODEL_NAME')
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
batch_size = 32

# Function to extract text from PDF file with error handling
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        return ' '.join(page.extract_text() for page in reader.pages)
    except PyPDF2.errors.PdfReadError as e:
        print(f"Error reading PDF file {pdf_file}: {e}")
        return ""  # Return empty string if PDF can't be read
    except Exception as e:
        print(f"Unexpected error with file {pdf_file}: {e}")
        return ""

# Function to split the text into smaller chunks
def split_text(text, max_chunk_size=512, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size, 
        chunk_overlap=chunk_overlap
    )
    documents = text_splitter.create_documents([text])
    return [doc.page_content for doc in documents]

# Function to generate embeddings from text
def embed_text(text: str):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

# Function to upload vectors to Pinecone
def upload_to_pinecone(vectors, namespace="ns1"):
    index.upsert(vectors=vectors, namespace=namespace)

# Function to process PDF and upload to Pinecone
def process_pdf_and_upload(pdf_file, namespace="ns1"):
    pdf_name = os.path.basename(pdf_file)  # Get the PDF file name
    text = extract_text_from_pdf(pdf_file)
    document_chunks = split_text(text)
    vectors_to_upsert = []
    
    for batch_index in range(0, len(document_chunks), batch_size):
        batch = document_chunks[batch_index:batch_index + batch_size]
        for chunk_index, chunk in enumerate(batch):
            embedding = embed_text(chunk).squeeze().tolist()
            vector = {
                "id": f"{pdf_name}-chunk-{batch_index + chunk_index}",
                "values": embedding,
                "metadata": {"chunk": chunk}
            }
            vectors_to_upsert.append(vector)
        upload_to_pinecone(vectors=vectors_to_upsert, namespace=namespace)
        vectors_to_upsert.clear()
    return len(document_chunks)

# Function to traverse directories and process all PDFs
def upload_pdfs_in_directory(directory_path, namespace="ns1"):
    total_chunks_uploaded = 0
    # Traverse the directory and subdirectories for PDF files
    for root, dirs, files in os.walk(directory_path):
        pdf_files = [f for f in files if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(root, pdf_file)
            print(f"Processing {pdf_path}...")
            chunks_uploaded = process_pdf_and_upload(pdf_path, namespace)
            total_chunks_uploaded += chunks_uploaded
    return total_chunks_uploaded

# Example usage
directory_path = "/Users/noel/pmc_pdfs/batch"
uploaded_chunks = upload_pdfs_in_directory(directory_path)
print(f"Total chunks uploaded: {uploaded_chunks}")
