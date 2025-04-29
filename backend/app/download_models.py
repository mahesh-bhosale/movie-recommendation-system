# app/download_models.py

import os
import requests
import logging
import sys
from pathlib import Path
import time
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_confirm_token(response):
    """Get the confirmation token from Google Drive's download page"""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def download_file(url, output_path):
    """Download a file from Google Drive with confirmation handling"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading {output_path} (attempt {attempt + 1}/{max_retries})")
            
            # First request to get the confirmation token
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Check if we need to confirm the download
            token = get_confirm_token(response)
            if token:
                logger.info("Confirming download...")
                params = {'id': url.split('id=')[1], 'confirm': token}
                response = requests.get(url, params=params, stream=True)
                response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / total_size) if total_size > 0 else 0
                    logger.info(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
            
            logger.info(f"Successfully downloaded {output_path}")
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
    files = {
        "movie_dict.pkl": "https://drive.google.com/uc?export=download&id=1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
        "simi.pkl": "https://drive.google.com/uc?export=download&id=1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
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
    
    # Verify all files exist
    missing_files = [f for f in files.keys() if not (folder / f).exists()]
    if missing_files:
        raise Exception(f"Missing model files after download: {missing_files}")
    
    logger.info("All model files downloaded successfully")

if __name__ == "__main__":
    download_models()
