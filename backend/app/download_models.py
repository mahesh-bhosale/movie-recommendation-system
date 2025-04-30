# app/download_models.py

import os
import logging
import sys
from pathlib import Path
import pickle
import gdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def verify_pickle_file(file_path):
    """Verify that a file is a valid pickle file."""
    try:
        with open(file_path, 'rb') as f:
            pickle.load(f)
        return True
    except Exception as e:
        logger.error(f"Invalid pickle file {file_path}: {e}")
        return False

def download_file(url, output_path):
    """Download a file from Google Drive using gdown."""
    try:
        logger.info(f"Downloading {output_path} using gdown")
        gdown.download(url, output_path, quiet=False)
        if not verify_pickle_file(output_path):
            raise Exception(f"Downloaded file {output_path} is not a valid pickle file")
        logger.info(f"Downloaded and verified: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Download failed for {output_path}: {e}")
        return False

def download_models():
    files = {
        "movie_dict.pkl": "https://drive.google.com/uc?id=1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
        "simi.pkl": "https://drive.google.com/uc?id=1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
    }

    folder = Path(__file__).parent / "ml_model"
    folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Model download directory: {folder}")

    for filename, url in files.items():
        path = folder / filename
        if path.exists():
            logger.info(f"{filename} already exists. Skipping.")
        else:
            if not download_file(url, str(path)):
                raise Exception(f"Failed to download or verify {filename}")

    # Final check: ensure all files are present and valid
    for filename in files:
        path = folder / filename
        if not path.exists():
            raise Exception(f"Missing file: {filename}")
        if not verify_pickle_file(path):
            raise Exception(f"Corrupted file: {filename}")

    logger.info("✅ All model files downloaded and verified successfully.")

if __name__ == "__main__":
    download_models()
