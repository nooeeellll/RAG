import ftplib
import os
import time
from datetime import datetime
import logging
from pathlib import Path
import concurrent.futures
import re

class PMCScraper:
    def __init__(self, base_dir="pmc_pdfs"):
        self.ftp_host = "ftp.ncbi.nlm.nih.gov"
        self.base_path = "/pub/pmc/oa_pdf/00"
        self.base_dir = Path(base_dir)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging to both file and console."""
        self.base_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / 'scraper.log'),
                logging.StreamHandler()
            ]
        )
        
    def connect_ftp(self):
        """Establish FTP connection with error handling."""
        try:
            ftp = ftplib.FTP(self.ftp_host)
            ftp.login()  # anonymous login
            return ftp
        except ftplib.all_errors as e:
            logging.error(f"FTP connection failed: {str(e)}")
            raise
            
    def get_subdirectories(self, ftp, path):
        """List all subdirectories in the given FTP path."""
        try:
            dirs = []
            ftp.cwd(path)
            ftp.dir(lambda x: dirs.append(x.split()[-1]))
            return [d for d in dirs if re.match(r'^[0-9a-f]{2}$', d)]
        except ftplib.all_errors as e:
            logging.error(f"Failed to get subdirectories for {path}: {str(e)}")
            return []
            
    def download_pdf(self, ftp, remote_path, local_path):
        """Download a single PDF file."""
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except ftplib.all_errors as e:
            logging.error(f"Failed to download {remote_path}: {str(e)}")
            return False
            
    def process_directory(self, subdir):
        """Process a single directory and download its PDFs."""
        try:
            ftp = self.connect_ftp()
            dir_path = f"{self.base_path}/{subdir}"
            local_dir = self.base_dir / subdir
            
            # Get list of PDF files in directory
            ftp.cwd(dir_path)
            files = []
            ftp.dir(lambda x: files.append(x.split()[-1]) if x.endswith('.pdf') else None)
            
            # Download each PDF
            for pdf_file in files:
                remote_path = f"{dir_path}/{pdf_file}"
                local_path = local_dir / pdf_file
                
                if local_path.exists():
                    logging.info(f"Skipping existing file: {pdf_file}")
                    continue
                    
                if self.download_pdf(ftp, remote_path, local_path):
                    logging.info(f"Successfully downloaded: {pdf_file}")
                time.sleep(0.5)  # Rate limiting
                
            ftp.quit()
            return len(files)
        except Exception as e:
            logging.error(f"Error processing directory {subdir}: {str(e)}")
            return 0
            
    def run(self, max_workers=4):
        """Main method to run the scraper with parallel processing."""
        try:
            # Get list of all subdirectories
            ftp = self.connect_ftp()
            subdirs = self.get_subdirectories(ftp, self.base_path)
            ftp.quit()
            
            logging.info(f"Found {len(subdirs)} subdirectories to process")
            
            # Process directories in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_dir = {executor.submit(self.process_directory, subdir): subdir 
                               for subdir in subdirs}
                
                total_files = 0
                for future in concurrent.futures.as_completed(future_to_dir):
                    subdir = future_to_dir[future]
                    try:
                        files_downloaded = future.result()
                        total_files += files_downloaded
                        logging.info(f"Completed directory {subdir}: {files_downloaded} files")
                    except Exception as e:
                        logging.error(f"Directory {subdir} generated an exception: {str(e)}")
            
            logging.info(f"Scraping completed. Total files downloaded: {total_files}")
            
        except Exception as e:
            logging.error(f"Scraper failed: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = PMCScraper()
    scraper.run()