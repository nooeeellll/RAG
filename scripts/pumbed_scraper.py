import ftplib
import os
import time
from datetime import datetime
import logging
from pathlib import Path
import concurrent.futures
import re

class PMCScraper:
    # Define available sources and their paths
    SOURCES = {
        'PMC': '/pub/pmc/oa_pdf/00',
        'NLM': '/pub/litarch'
    }

    def __init__(self, base_dir="knowledge_base", source="PMC"):
        self.ftp_host = "ftp.ncbi.nlm.nih.gov"
        if source not in self.SOURCES:
            raise ValueError(f"Invalid source. Choose from: {', '.join(self.SOURCES.keys())}")
        self.source = source
        self.base_path = self.SOURCES[source]
        self.base_dir = Path(base_dir)
        self.source_dir = self.base_dir / source  # Create source-specific directory path
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging to both file and console."""
        self.base_dir.mkdir(exist_ok=True)
        self.source_dir.mkdir(exist_ok=True)  # Create source-specific directory
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.source_dir / 'scraper.log'),  # Log in source directory
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
            
    def download_file(self, ftp, remote_path, local_path):
        """Download a single file."""
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except ftplib.all_errors as e:
            logging.error(f"Failed to download {remote_path}: {str(e)}")
            return False
            
    def is_directory(self, ftp, name):
        """Check if the item is a directory."""
        current = ftp.pwd()
        try:
            ftp.cwd(name)
            ftp.cwd(current)
            return True
        except ftplib.error_perm:
            return False

    def list_files_recursive(self, ftp, path):
        """Recursively list all files in the directory and its subdirectories."""
        files = []
        directories = []
        
        try:
            ftp.cwd(path)
            items = []
            ftp.dir(lambda x: items.append(x.split()[-1]))
            
            for item in items:
                if item in ['.', '..']:
                    continue
                    
                full_path = f"{path}/{item}"
                if self.is_directory(ftp, item):
                    directories.append(full_path)
                else:
                    files.append(full_path)
            
            # Recursively process subdirectories
            for directory in directories:
                files.extend(self.list_files_recursive(ftp, directory))
                
            return files
            
        except ftplib.error_perm as e:
            logging.error(f"Permission error accessing {path}: {str(e)}")
            return []
            
    def process_directory(self, subdir):
        """Process a directory and its subdirectories."""
        try:
            ftp = self.connect_ftp()
            dir_path = f"{self.base_path}/{subdir}"
            local_dir = self.source_dir / subdir  # Use source-specific directory
            
            # Get list of all files recursively
            files = self.list_files_recursive(ftp, dir_path)
            
            # Download each file
            downloaded = 0
            for remote_path in files:
                # Convert remote path to local path structure
                relative_path = remote_path.replace(dir_path, '')
                local_path = local_dir / relative_path.lstrip('/')
                
                if local_path.exists():
                    logging.info(f"Skipping existing file: {local_path}")
                    continue
                
                if self.download_file(ftp, remote_path, local_path):
                    extension = Path(remote_path).suffix
                    logging.info(f"Successfully downloaded: {remote_path} (type: {extension})")
                    downloaded += 1
                time.sleep(0.5)  # Rate limiting
                
            ftp.quit()
            return downloaded
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

    @staticmethod
    def get_source_selection():
        """Get and validate source selection from user."""
        while True:
            print("\nAvailable sources:")
            for i, source in enumerate(PMCScraper.SOURCES.keys(), 1):
                print(f"{i}. {source}")
            try:
                choice = int(input("\nSelect source number (0 to exit): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(PMCScraper.SOURCES):
                    return list(PMCScraper.SOURCES.keys())[choice - 1]
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

if __name__ == "__main__":
    while True:
        selected_source = PMCScraper.get_source_selection()
        if selected_source is None:
            break
            
        print(f"\nStarting scraper for {selected_source}...")
        scraper = PMCScraper(source=selected_source)
        scraper.run()
        
        if input("\nWould you like to scrape another source? (y/n): ").lower() != 'y':
            break
    
    print("\nScraping completed. Goodbye!")