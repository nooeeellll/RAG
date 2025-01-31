import os
import tarfile

def extract_pdf_from_tar_gz(source_dir, target_dir):
    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Recursively search for .tar.gz files in the source directory
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.endswith('.tar.gz'):
                tar_gz_path = os.path.join(root, filename)
                
                try:
                    # Open the tar.gz file
                    with tarfile.open(tar_gz_path, 'r:gz') as tar:
                        # Extract only .pdf files
                        for member in tar.getmembers():
                            if member.name.endswith('.pdf'):
                                # Define the path to extract the PDF to the target directory
                                pdf_path = os.path.join(target_dir, os.path.basename(member.name))
                                print(f'Extracting {pdf_path}')
                                tar.extract(member, path=target_dir)
                except Exception as e:
                    print(f"Error extracting from {filename}: {e}")

if __name__ == '__main__':
    source_dir = 'knowledge_base/NLM'  # Source directory with tar.gz files
    target_dir = 'knowledge_base/NLM_PDFs'  # Target directory for extracted PDFs
    extract_pdf_from_tar_gz(source_dir, target_dir)
