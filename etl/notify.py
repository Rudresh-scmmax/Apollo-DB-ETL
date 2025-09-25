from __future__ import annotations

import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_run_report(run_dir: str, run_id: str) -> None:
    to_email = os.getenv('REPORT_TO_EMAIL')
    from_email = os.getenv('REPORT_FROM_EMAIL') or os.getenv('SMTP_USER')
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not (to_email and smtp_host and smtp_user and smtp_pass):
        return  # Missing config; skip emailing

    # Support multiple recipients (comma-separated)
    to_emails = [email.strip() for email in to_email.split(',') if email.strip()]

    subject = f"APOLLO ETL Report - {run_id}"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)  # Display all recipients
    msg['Subject'] = subject

    # Attach summary HTML inline-friendly
    summary_path = os.path.join(run_dir, 'summary.html')
    with open(summary_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    msg.attach(MIMEText(html_content, 'html'))

    # Attach any rejected CSVs
    for path in glob.glob(os.path.join(run_dir, 'rejected_*.csv')):
        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg, to_addrs=to_emails)
    except Exception:
        # Best-effort: swallow email errors so ETL doesn't fail on notification
        pass


