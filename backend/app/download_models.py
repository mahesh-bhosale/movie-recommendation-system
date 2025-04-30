# app/download_models.py

import os
import requests
import logging
import sys
from pathlib import Path
import time
import pickle
import gdown

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_pickle_file(file_path):
    """Verify that a file is a valid pickle file"""
    try:
        with open(file_path, 'rb') as f:
            pickle.load(f)
        return True
    except Exception as e:
        logger.error(f"Error verifying pickle file {file_path}: {str(e)}")
        return False

def download_file(url, output_path):
    """Download a file from Google Drive using requests"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading {output_path} (attempt {attempt + 1}/{max_retries})")
            
            # Extract file ID from URL
            file_id = url.split('id=')[1]
            
            # First request to get the download URL
            session = requests.Session()
            response = session.get(url, allow_redirects=True)
            
            # Get the download URL from the response
            download_url = response.url
            
            # Download the file
            response = session.get(download_url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify the downloaded file
            if not verify_pickle_file(output_path):
                raise Exception(f"Downloaded file {output_path} is not a valid pickle file")
            
            logger.info(f"Successfully downloaded and verified {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {output_path}: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise
    return False

def download_models():
    # Use direct download links with proper format
    files = {
        "movie_dict.pkl": "https://drive.google.com/uc?id=1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
        "simi.pkl": "https://drive.google.com/uc?id=1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
    }

    # Get the absolute path to the ml_model directory
    current_dir = Path(__file__).parent
    folder = current_dir / "ml_model"
    
    # Create directory if it doesn't exist
    folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading models to: {folder}")
    
    for filename, url in files.items():
        path = folder / filename
        if not path.exists():
            try:
                if download_file(url, str(path)):
                    logger.info(f"Successfully downloaded {filename}")
                else:
                    raise Exception(f"Failed to download {filename}")
            except Exception as e:
                logger.error(f"Error downloading {filename}: {str(e)}")
                raise
        else:
            logger.info(f"{filename} already exists. Skipping download.")
    
    # Verify all files exist and are valid pickle files
    missing_files = [f for f in files.keys() if not (folder / f).exists()]
    if missing_files:
        raise Exception(f"Missing model files after download: {missing_files}")
    
    # Verify all files are valid pickle files
    invalid_files = [f for f in files.keys() if not verify_pickle_file(folder / f)]
    if invalid_files:
        raise Exception(f"Invalid pickle files: {invalid_files}")
    
    logger.info("All model files downloaded and verified successfully")

if __name__ == "__main__":
    download_models()
