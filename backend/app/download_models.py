import os
import time
import pickle
import requests
from pathlib import Path
from tqdm import tqdm

def is_valid_pickle(file_path):
    """Check if a file is a valid pickle file."""
    try:
        with open(file_path, 'rb') as f:
            pickle.load(f)
        return True
    except Exception:
        return False

def download_file(url, output_path, chunk_size=8192, min_size=None):
    """
    Download a file from a URL with progress bar.
    Handles Google Drive's large file download confirmation.
    
    Args:
        url (str): URL to download from
        output_path (Path): Path to save the file
        chunk_size (int): Size of chunks to download at a time
        min_size (int): Minimum expected file size in bytes
    """
    session = requests.Session()
    
    # First request to get the confirmation token
    response = session.get(url, stream=True)
    response.raise_for_status()
    
    # Check if we got a confirmation page
    if 'text/html' in response.headers.get('content-type', ''):
        # Extract the confirmation token
        confirm_token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                confirm_token = value
                break
        
        if confirm_token:
            # Make the actual download request with the confirmation token
            url = f"{url}&confirm={confirm_token}"
            response = session.get(url, stream=True)
            response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    # For large files, we'll check the size after download
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path.name,
        total=total_size if total_size > 0 else None,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                size = f.write(chunk)
                pbar.update(size)
    
    # Wait for file to be fully written
    time.sleep(2)
    
    # Check file size after download
    file_size = output_path.stat().st_size
    if min_size and file_size < min_size:
        # If we got a small file, it might be an HTML error page
        with open(output_path, 'rb') as f:
            content = f.read(1024)
            if b'<html' in content.lower():
                raise ValueError("Received HTML response instead of file data")
        raise ValueError(f"Downloaded file size ({file_size} bytes) is smaller than minimum expected size ({min_size} bytes)")
    
    return file_size

def download_from_drive(file_id, output, retries=3, min_size=None):
    """
    Download a file from Google Drive.
    
    Args:
        file_id (str): Google Drive file ID
        output (str): Path to save the downloaded file
        retries (int): Number of times to retry the download on failure
        min_size (int): Minimum expected file size in bytes
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists and is valid
    if output.exists():
        current_size = output.stat().st_size
        if min_size and current_size >= min_size:
            if is_valid_pickle(output):
                print(f"✅ {output.name} already exists and is valid")
                return str(output)
            else:
                print(f"⚠️ {output.name} exists but is corrupted, will redownload")
                output.unlink()
        elif current_size > 0:
            print(f"⚠️ {output.name} exists but size mismatch, will redownload")
            output.unlink()
    
    # Google Drive direct download URL
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            print(f"Download attempt {attempt}...")
            downloaded_size = download_file(url, output, min_size=min_size)
            
            if not output.exists():
                raise ValueError("Download failed - file not created")
                
            # Verify the file size
            file_size = output.stat().st_size
            if file_size == 0:
                raise ValueError("Downloaded file is empty")
            print(f"Downloaded file size: {file_size / (1024*1024):.2f} MB")
            
            # Adaptive wait time for large files
            if file_size > 50 * 1024 * 1024:  # > 50MB
                wait_time = min(60, int(file_size / (5 * 1024 * 1024)))  # 1s per 5MB, max 60s
                print(f"Waiting {wait_time} seconds for file to be fully written...")
                time.sleep(wait_time)
                
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
            model_dir / "movie_dict.pkl",
            min_size=2000000  # Minimum size: ~2MB
        )
        print("✅ movie_dict.pkl downloaded and verified.")
        
        # Download simi.pkl
        print("Downloading simi.pkl...")
        download_from_drive(
            "1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
            model_dir / "simi.pkl",
            min_size=170 * 1024 * 1024  # Minimum size: 170MB (actual size is ~176MB)
        )
        print("✅ simi.pkl downloaded and verified.")
        
    except Exception as e:
        print(f"❌ Error during model download: {e}")
        raise

if __name__ == "__main__":
    download_models()
