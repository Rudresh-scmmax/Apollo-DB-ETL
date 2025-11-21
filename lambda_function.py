import os
import sys
import shutil
import boto3
import urllib.parse
import time

# Import the ETL runner directly instead of subprocess
from etl import run_etl

s3_client = boto3.client("s3")

def log(msg: str):
    """Helper to print logs with timestamp for easier debugging."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def lambda_handler(event, context):
    log("=== Lambda triggered ===")
    log(f"Event received: {event}")

    record = event["Records"][0]["s3"]
    bucket = record["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["object"]["key"])
    log(f"Processing S3 event for bucket={bucket}, key={key}")

    # ✅ Ignore events from reports/ to avoid recursion
    if key.startswith("reports/"):
        log(f"Skipping report file trigger: {key}")
        return {"statusCode": 200, "message": "Skipped report file"}

    excel_file = f"/tmp/{os.path.basename(key)}"
    log(f"Downloading {bucket}/{key} -> {excel_file}")
    s3_client.download_file(bucket, key, excel_file)
    log("Download complete")

    reports_dir = "/tmp/reports"
    os.makedirs(reports_dir, exist_ok=True)
    log(f"Reports directory ready: {reports_dir}")

    stdout, stderr = "", ""
    try:
        # Build arguments for run_etl.main
        sys_argv = [
            "--mode", "incremental",
            "--excel", excel_file,
            "--reports-dir", reports_dir,
        ]
        log(f"Starting ETL with args: {sys_argv}")

        # Run ETL directly
        start = time.time()
        run_etl.main(sys_argv)
        elapsed = time.time() - start
        log(f"ETL finished successfully in {elapsed:.2f} seconds")

        # ✅ Upload all report files to S3 under reports/<run_id>/
        run_id = None
        for root, _, files in os.walk(reports_dir):
            for f in files:
                local_path = os.path.join(root, f)
                if run_id is None:
                    run_id = os.path.basename(os.path.dirname(local_path))
                s3_key = f"reports/{run_id}/{f}"
                log(f"Uploading report: {local_path} -> s3://{bucket}/{s3_key}")
                s3_client.upload_file(local_path, bucket, s3_key)

    except Exception as e:
        stderr = str(e)
        log(f"ETL FAILED: {stderr}")
        raise
    finally:
        log("Cleaning up local files")
        if os.path.exists(excel_file):
            os.remove(excel_file)
            log(f"Removed {excel_file}")
        if os.path.exists(reports_dir):
            shutil.rmtree(reports_dir)
            log(f"Removed reports directory {reports_dir}")

    return {
        "statusCode": 200,
        "stdout": stdout,
        "stderr": stderr,
    }
