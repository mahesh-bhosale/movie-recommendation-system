import os
import re
import time
import pickle
import gdown
from pathlib import Path

def download_from_drive(file_id, output, retries=3, quiet=False):
    """
    Download a file from Google Drive using gdown.
    
    Args:
        file_id (str): Google Drive file ID
        output (str): Path to save the downloaded file
        retries (int): Number of times to retry the download on failure
        quiet (bool): If True, suppress progress output from gdown

    Returns:
        str: Path to the downloaded file

    Raises:
        RuntimeError: If the file cannot be downloaded or is corrupted
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            # Use gdown's more robust download method for large files
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url=url, output=str(output), quiet=quiet, fuzzy=True)
            
            if not output.exists():
                raise ValueError("Download failed - file not created")
                
            # Verify the file size
            if output.stat().st_size == 0:
                raise ValueError("Downloaded file is empty")
                
            # Verify pickle file if applicable
            if output.suffix.lower() == '.pkl':
                try:
                    with open(output, 'rb') as f:
                        pickle.load(f)
                except Exception as e:
                    raise ValueError(f"Downloaded pickle file is corrupted: {e}")
            
            return str(output)
            
        except Exception as e:
            last_exception = e
            print(f"Download attempt {attempt} failed: {e}")
            
            if output.exists():
                output.unlink()
                
            if attempt < retries:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                raise RuntimeError(f"Failed to download file after {retries} attempts: {last_exception}")

def download_models():
    """
    Download all required model files from Google Drive.
    Creates the necessary directory structure and downloads the files.
    """
    try:
        # Create model directory
        model_dir = Path("app/ml_model")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Download movie_dict.pkl
        print("Downloading movie_dict.pkl...")
        download_from_drive(
            "1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
            model_dir / "movie_dict.pkl"
        )
        print("✅ movie_dict.pkl downloaded and verified.")
        
        # Download simi.pkl
        print("Downloading simi.pkl...")
        download_from_drive(
            "1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
            model_dir / "simi.pkl"
        )
        print("✅ simi.pkl downloaded and verified.")
        
    except Exception as e:
        print(f"❌ Error during model download: {e}")
        raise

if __name__ == "__main__":
    download_models()
