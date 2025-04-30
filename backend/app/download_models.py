import os
import re
import time
import pickle
from urllib.parse import urlparse, parse_qs

import gdown

def download_from_drive(link_or_id, output, retries=3, quiet=False):
    """
    Download a file from Google Drive using gdown.
    Accepts either a file ID or a full share URL.

    Args:
        link_or_id (str): Google Drive file ID or full share URL.
        output (str): Path to save the downloaded file.
        retries (int): Number of times to retry the download on failure.
        quiet (bool): If True, suppress progress output from gdown.

    Returns:
        str: Path to the downloaded file.

    Raises:
        RuntimeError: If the file cannot be downloaded or is corrupted.
    """
    # Determine if the input is a URL or a file ID
    is_url = bool(re.match(r'^https?://', link_or_id))
    file_id = None
    url = link_or_id

    if is_url:
        # Try to extract file ID from various Google Drive URL formats
        patterns = [
            r'/d/([A-Za-z0-9_-]+)',  # Standard format
            r'id=([A-Za-z0-9_-]+)',  # URL parameter format
            r'file/d/([A-Za-z0-9_-]+)',  # Alternative format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link_or_id)
            if match:
                file_id = match.group(1)
                break
        
        if not file_id:
            raise ValueError(f"Could not extract file ID from URL: {link_or_id}")
    else:
        file_id = link_or_id

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            if is_url:
                # Try with direct URL first
                try:
                    downloaded = gdown.download(url=url, output=output, quiet=quiet, fuzzy=True)
                except Exception as e:
                    print(f"Direct URL download failed: {e}")
                    # Fall back to file ID if URL fails
                    downloaded = gdown.download(id=file_id, output=output, quiet=quiet)
            else:
                downloaded = gdown.download(id=file_id, output=output, quiet=quiet)

            if downloaded is None or not os.path.exists(output):
                raise ValueError("gdown download failed or returned no file")

            break  # Download succeeded

        except Exception as e:
            last_exception = e
            print(f"Download attempt {attempt} failed: {e}")

            if os.path.exists(output):
                os.remove(output)

            if attempt < retries:
                time.sleep(1)
                continue
            else:
                raise RuntimeError(f"Failed to download file after {retries} attempts: {last_exception}")

    # Verify downloaded file if it's a pickle
    if output.lower().endswith('.pkl'):
        try:
            with open(output, 'rb') as f:
                pickle.load(f)
        except Exception as e:
            if os.path.exists(output):
                os.remove(output)
            raise RuntimeError(f"Downloaded pickle file is corrupted: {e}")

    return output

def download_models():
    """
    Download all required model files from Google Drive.
    Creates the necessary directory structure and downloads the files.
    """
    try:
        os.makedirs("app/ml_model", exist_ok=True)

        # Using direct file IDs instead of URLs
        download_from_drive(
            "1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",  # movie_dict.pkl file ID
            "app/ml_model/movie_dict.pkl"
        )
        print("✅ movie_dict.pkl downloaded and verified.")

        download_from_drive(
            "1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",  # simi.pkl file ID
            "app/ml_model/simi.pkl"
        )
        print("✅ simi.pkl downloaded and verified.")

    except Exception as e:
        print(f"❌ Error during model download: {e}")
        raise

if __name__ == "__main__":
    download_models()
