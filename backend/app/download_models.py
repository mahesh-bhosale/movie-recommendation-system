# app/download_models.py

import os
import gdown
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def download_models():
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
            logger.info(f"Downloading {filename}...")
            try:
                gdown.download(url, str(path), quiet=False)
                if path.exists():
                    logger.info(f"Successfully downloaded {filename}")
                else:
                    logger.error(f"Failed to download {filename}")
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
