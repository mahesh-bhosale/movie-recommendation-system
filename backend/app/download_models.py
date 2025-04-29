# app/download_models.py

import os
import gdown

files = {
    "movie_dict.pkl": "https://drive.google.com/uc?id=1XraEXCrqAr_8JR11ZGA2Gxe2QYHxy8lu",
    "simi.pkl": "https://drive.google.com/uc?id=1z48JOfbPcYLfZzbr9ax0lBqTDtND0Bvn",
}

folder = os.path.dirname(__file__) + "/ml_model"

for filename, url in files.items():
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        print(f"Downloading {filename}...")
        gdown.download(url, path, quiet=False)
    else:
        print(f"{filename} already exists. Skipping download.")
