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

### Note
This script is **separate from the ETL pipeline**. It's only used locally to create Excel templates. The actual ETL processing happens in Lambda (see `lambda_function.py` in the root directory).

