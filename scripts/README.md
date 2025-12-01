# Scripts

This folder contains utility scripts that are **not part of the ETL pipeline**.

## Excel Template Generator

**`generate_excel_from_models.py`** - Generate Excel templates from database models

### Purpose
Create Excel template files with proper column headers for data entry. This is a **local development tool** used to generate Excel files before uploading them to S3 for Lambda processing.

### Usage

```bash
# From project root
python scripts/generate_excel_from_models.py --models-path etl/models.py --output apollo_template.xlsx
```

### What It Does
- Reads all tables from `etl/models.py`
- Creates one Excel sheet per table
- Each sheet contains column headers (empty rows for data entry)
- Optionally includes a Summary sheet with table information

### Output
- Excel file with empty sheets and column headers
- Column names match database column names exactly
- Ready for data entry

---

## Database Export Tool

**`export_db_to_excel.py`** - Export all data from database to Excel

### Purpose
Export all data from a PostgreSQL database to an Excel file. Useful for backups, data analysis, or creating data snapshots.

### Usage

```bash
# From project root
python scripts/export_db_to_excel.py --db-url "postgresql://user:pass@host:port/db" --output export.xlsx
```

### What It Does
- Connects to PostgreSQL database
- Scans all tables in the database
- Exports data from each table to a separate Excel sheet
- **Skips empty tables** (tables with 0 rows)
- Handles timezone-aware datetimes (converts to timezone-naive for Excel compatibility)

### Output
- Excel file with one sheet per table that has data
- All rows and columns from each table
- Summary of tables exported and skipped

### Example

```bash
python scripts/export_db_to_excel.py \
    --db-url "postgresql://postgres:password@localhost:5432/apollo" \
    --output apollo_data_export.xlsx
```

### Note
This script is **separate from the ETL pipeline**. It's a utility tool for data export/backup purposes.

