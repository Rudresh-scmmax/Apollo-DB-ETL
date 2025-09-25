import os
import subprocess

def lambda_handler(event, context):
    excel_path = os.getenv("EXCEL_PATH", "Data_processedv4.xlsx")
    reports_dir = os.getenv("REPORTS_DIR", "/tmp/reports")


    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join("/var/task", excel_path)



    # Equivalent of running your CLI
    cmd = [
        "python",
        "-m",
        "etl.run_etl",
        "--mode", "incremental",
        "--excel", excel_file,
        "--reports-dir", reports_dir
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    return {
        "statusCode": 200,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
