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
        parsed = urlparse(link_or_id)
        query_params = parse_qs(parsed.query)
        if 'id' in query_params:
            file_id = query_params['id'][0]
        else:
            match = re.search(r'/d/([A-Za-z0-9_-]+)', link_or_id)
            if match:
                file_id = match.group(1)
    else:
        file_id = link_or_id

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            if is_url:
                downloaded = gdown.download(url=url, output=output, quiet=quiet, fuzzy=True)
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
                if is_url and file_id and attempt == 1:
                    print("Retrying using extracted file ID instead of URL")
                    is_url = False
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

if __name__ == "__main__":
    try:
        os.makedirs("app/ml_model", exist_ok=True)

        download_from_drive(
            "https://drive.google.com/file/d/1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu/view?usp=sharing",
            "app/ml_model/movie_dict.pkl"
        )
        print("✅ movie_dict.pkl downloaded and verified.")

        download_from_drive(
            "https://drive.google.com/file/d/1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn/view?usp=sharing",
            "app/ml_model/simi.pkl"
        )
        print("✅ simi.pkl downloaded and verified.")

    except Exception as e:
        print(f"❌ Error during model download: {e}")
