import base64
import io
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_uploaded_files(contents_list, filenames_list, process_func):
    if not contents_list or not filenames_list:
        return [], 0
    
    results = []
    total_chunks = 0
    
    # Convert contents to file-like objects
    pdf_files = []
    for content, filename in zip(contents_list, filenames_list):
        try:
            # Decode the base64 content
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # Create a file-like object
            pdf_file = io.BytesIO(decoded)
            pdf_file.name = filename  # Add name attribute for metadata
            pdf_files.append(pdf_file)
            
        except Exception as e:
            results.append({
                'filename': filename,
                'status': 'error',
                'error': str(e),
                'chunks': 0
            })
    
    try:
        # Process all PDF files at once
        if pdf_files:
            chunks_per_file = process_func(pdf_files)  # Now expecting a dictionary
            for pdf_file in pdf_files:
                file_chunks = chunks_per_file.get(pdf_file.name, 0)
                results.append({
                    'filename': pdf_file.name,
                    'status': 'success',
                    'chunks': file_chunks,
                    'error': None
                })
                total_chunks += file_chunks
                
    except Exception as e:
        for pdf_file in pdf_files:
            results.append({
                'filename': pdf_file.name,
                'status': 'error',
                'error': str(e),
                'chunks': 0
            })
    
    return results, total_chunks

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return ' '.join(page.extract_text() for page in reader.pages)

def split_text(text, max_chunk_size=512, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size, 
        chunk_overlap=chunk_overlap
    )
    documents = text_splitter.create_documents([text])
    return [doc.page_content for doc in documents]