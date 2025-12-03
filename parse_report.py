import pandas as pd
from pathlib import Path

# Read the latest report
report_path = Path("reports/2025-12-03_092039/summary.html")
html_content = report_path.read_text(encoding='utf-8')

# Extract key metrics
import re

# Extract overall status
overall_match = re.search(r'Overall Status: ([^<\n]+)', html_content)
overall_status = overall_match.group(1) if overall_match else "Unknown"

# Extract total records
total_match = re.search(r'Total Records Processed: (\d+)', html_content)
total_records = total_match.group(1) if total_match else "Unknown"

# Extract successfully loaded
success_match = re.search(r'Successfully Loaded: (\d+)', html_content)
success_loaded = success_match.group(1) if success_match else "Unknown"

# Extract rejected
rejected_match = re.search(r'Rejected Records: (\d+)', html_content)
rejected_records = rejected_match.group(1) if rejected_match else "Unknown"

print("=" * 80)
print("ETL RUN SUMMARY")
print("=" * 80)
print(f"Overall Status: {overall_status}")
print(f"Total Records Processed: {total_records}")
print(f"Successfully Loaded: {success_loaded}")
print(f"Rejected Records: {rejected_records}")
print()

# Find master tables in the report
master_tables = ['uom_master', 'material_master', 'currency_master', 'material_type_master', 
                 'location_type_master', 'supplier_master', 'calendar_master']

print("=" * 80)
print("MASTER TABLES STATUS")
print("=" * 80)

for table in master_tables:
    # Look for table row in HTML
    pattern = rf'<td>{table}</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>([^<]+)</td>'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        records_read, loaded, rejected, new_records, updated, status = match.groups()
        status_icon = "✓" if "SUCCESS" in status else ("⚠" if "PARTIAL" in status else "✗")
        print(f"{status_icon} {table:30s} | Read: {records_read:4s} | Loaded: {loaded:4s} | Rejected: {rejected:4s}")
    else:
        print(f"? {table:30s} | Not found in report")

print()
