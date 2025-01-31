import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import io

# Add project root to Python path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.embedding import EmbeddingManager
from core.utils import extract_text_from_pdf, split_text

load_dotenv()

# Get the current script's directory and set knowledge_base path
current_dir = Path(__file__).parent.parent
directory_path = current_dir / "knowledge_base"

def upload_pdfs_in_directory(directory_path, namespace="ns1"):
    """Process and upload all PDFs in a directory to Pinecone."""
    embedding_manager = EmbeddingManager()
    total_chunks_uploaded = 0
    
    # Traverse the directory and subdirectories for PDF files
    for root, dirs, files in os.walk(directory_path):
        pdf_files = []
        for file in files:
            if file.endswith('.pdf'):
                file_path = Path(os.path.join(root, file))
                # Read the file content
                with open(file_path, 'rb') as f:
                    content = f.read()
                # Create BytesIO object with the content
                pdf_file = io.BytesIO(content)
                # Add name attribute to the BytesIO object
                setattr(pdf_file, 'name', file)
                pdf_files.append(pdf_file)
                print(f"Processing {file}...")
        
        if pdf_files:
            # Process batch of PDFs
            chunks_per_file = embedding_manager.process_pdfs_and_upload(
                pdf_files,
                extract_text_from_pdf,
                split_text,
                namespace
            )
            
            # Sum up total chunks
            total_chunks_uploaded += sum(chunks_per_file.values())
            
            # Print results for each file
            for filename, chunk_count in chunks_per_file.items():
                print(f"Processed {filename}: {chunk_count} chunks")
    
    return total_chunks_uploaded

if __name__ == "__main__":
    uploaded_chunks = upload_pdfs_in_directory(directory_path)
    print(f"Total chunks uploaded: {uploaded_chunks}")
