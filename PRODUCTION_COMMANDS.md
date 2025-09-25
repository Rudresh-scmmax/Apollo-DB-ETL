# APOLLO ETL - Production Commands

## 🚀 Daily Production Runs

### Full Pipeline (Recommended)
```bash
# Activate environment
source etl_env/bin/activate

# Load environment variables
set -a; source configs/.env; set +a

# Run full ETL pipeline
python -m etl.run_etl --mode incremental --excel "Data_processedv4.xlsx"
```

### Single Table Loads
```bash
# Load specific table
python -m etl.run_etl --tables material_master --mode incremental --excel "file.xlsx"

# Load multiple specific tables
python -m etl.run_etl --tables "material_master,supplier_master" --mode incremental --excel "file.xlsx"

# Load only master tables
python -m etl.run_etl --category masters --mode incremental --excel "file.xlsx"
```

### Initial/Fresh Load (Use carefully!)
```bash
# Complete fresh load (truncates and reloads all data)
python -m etl.run_etl --mode initial --excel "file.xlsx"

# Fresh load specific table
python -m etl.run_etl --tables plant_material_purchase_org_sup --mode initial --excel "file.xlsx"
```

## 📊 Reports & Monitoring

### Report Location
- Reports saved to: `reports/YYYY-MM-DD_HHMMSS/`
- Summary: `summary.html` 
- Rejected data: `rejected_*.csv`

### Email Notifications
- Configured via SMTP settings in `.env`
- Automatically sent after each ETL run
- Contains summary + attachments for rejected data

## ⚠️ Important Notes

### Data Quality
- Plant table loads ~1,705 valid rows, rejects ~2,938 (missing material references)
- This is expected - the ETL handles it gracefully
- Invalid data is documented in reports with business-friendly explanations

### Environment Setup
1. Ensure `.env` file exists with proper credentials
2. Virtual environment activated: `source etl_env/bin/activate`
3. Database schema already exists (no `--create-schema` needed)

### Troubleshooting
- Check report HTML files for detailed error explanations
- Rejected CSV files show exact rows that failed and why
- Email notifications include actionable next steps

