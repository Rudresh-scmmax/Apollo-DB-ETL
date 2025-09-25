from __future__ import annotations

import yaml
import boto3
import os

def download_excel_from_s3(bucket: str, key: str) -> str:
    s3 = boto3.client("s3")
    local_path = os.path.join("/tmp", os.path.basename(key))
    s3.download_file(bucket, key, local_path)
    return local_path


def load_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


