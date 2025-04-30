import os
import logging
import sys
from pathlib import Path
import pickle
import gdown

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def verify_pickle_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            pickle.load(f)
        return True
    except Exception as e:
        logger.error(f"Invalid pickle file {file_path}: {e}")
        return False

def download_file(url, output_path):
    try:
        logger.info(f"Downloading {output_path}")
        
        # Improved URL validation
        if "drive.google.com" not in url and "id=" not in url:
            raise ValueError("Invalid Google Drive URL format")
            
        gdown.download(url, output_path, quiet=False, fuzzy=True)
        
        if not os.path.exists(output_path):
            raise FileNotFoundError("Downloaded file not created")
            
        if not verify_pickle_file(output_path):
            raise Exception("Invalid pickle content")
            
        logger.info(f"Download successful: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return False

def download_models():
    files = {
        "movie_dict.pkl": "https://drive.google.com/uc?id=1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
        "simi.pkl": "https://drive.google.com/uc?id=1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
    }

    folder = Path(__file__).parent / "ml_model"
    folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Download directory: {folder}")

    for filename, url in files.items():
        path = folder / filename
        if path.exists():
            logger.info(f"Skipping existing file: {filename}")
            continue
            
        logger.info(f"Downloading {filename}")
        for attempt in range(3):  # Add retry mechanism
            if download_file(url, str(path)):
                break
            logger.warning(f"Attempt {attempt+1} failed for {filename}")
        else:
            raise Exception(f"Failed after 3 attempts: {filename}")

    logger.info("✅ All files downloaded and verified")

if __name__ == "__main__":
    try:
        download_models()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        sys.exit(1)