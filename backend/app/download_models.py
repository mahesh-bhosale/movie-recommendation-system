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

def validate_file_id(file_id):
    """Ensure valid Google Drive file ID format"""
    if not (len(file_id) == 33 and file_id.isalnum()):
        raise ValueError(f"Invalid Google Drive file ID: {file_id}")

def download_file(file_id, output_path):
    try:
        logger.info(f"Downloading {output_path} (ID: {file_id})")
        
        # Validate file ID format first
        validate_file_id(file_id)
        
        # First method: direct download using file ID
        try:
            gdown.download(id=file_id, output=output_path, quiet=False)
            if verify_file(output_path):
                return True
        except Exception as e:
            logger.warning(f"Direct download failed: {str(e)}")
        
        # Fallback method: use alternative URL format
        try:
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, output_path, quiet=False, fuzzy=True)
            return verify_file(output_path)
        except Exception as e:
            logger.error(f"Fallback download failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return False

def verify_file(path):
    """Check file exists and is valid pickle"""
    if not os.path.exists(path):
        raise FileNotFoundError("File not created")
    if not verify_pickle_file(path):
        raise ValueError("Invalid pickle content")
    return True

def verify_pickle_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            pickle.load(f)
        return True
    except Exception as e:
        logger.error(f"Invalid pickle file: {e}")
        return False

def download_models():
    files = {
        "movie_dict.pkl": "1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
        "simi.pkl": "1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
    }

    folder = Path(__file__).parent / "ml_model"
    folder.mkdir(parents=True, exist_ok=True)

    for filename, file_id in files.items():
        path = folder / filename
        if path.exists():
            if verify_pickle_file(path):
                logger.info(f"Valid file exists: {filename}")
                continue
            else:
                logger.warning(f"Removing corrupted file: {filename}")
                path.unlink()

        logger.info(f"Starting download: {filename}")
        for attempt in range(3):
            if download_file(file_id, str(path)):
                logger.info(f"Successfully downloaded {filename}")
                break
            logger.warning(f"Attempt {attempt+1} failed for {filename}")
            if path.exists():
                path.unlink()
        else:
            raise Exception(f"Failed after 3 attempts: {filename}")

    logger.info("✅ All files successfully downloaded and verified")

if __name__ == "__main__":
    try:
        download_models()
    except Exception as e:
        logger.critical(f"Setup failed: {str(e)}")
        sys.exit(1)