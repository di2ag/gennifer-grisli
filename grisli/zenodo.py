import requests
import csv
import io
import pandas as pd
import os

def load_file(zenodo_id, file_key, base_url="https://zenodo.org/api/records"):
    r = requests.get(f"{base_url}/{zenodo_id}").json()
    files = {f["key"]: f for f in r["files"]}
    f = files[file_key]
    download_link = f["links"]["self"]
    # Deduce type from extension
    _, file_type = os.path.splitext(f['key'])
    if file_type == '.json':
        return requests.get(download_link).json()
    if file_type  == '.csv':
        with requests.Session() as s:
            download = s.get(download_link)
            decoded_content = download.content.decode('utf-8')
            return pd.read_csv(io.StringIO(decoded_content), header=0, index_col=0)
    raise NotImplementedError(f'File type of: {ext} is not implemented.')
