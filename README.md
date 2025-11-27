# Apollo DB ETL

ETL system for processing Excel files and loading data into PostgreSQL database.

## Overview

This project consists of two main components:

1. **Local Excel Template Generation** - Create Excel templates from database models
2. **Lambda ETL Processing** - AWS Lambda function that processes uploaded Excel files and inserts data into the database

## Quick Start

### 1. Generate Excel Template (Local)

Create an Excel template file with all tables and column headers:

```bash
python scripts/generate_excel_from_models.py --models-path etl/models.py --output apollo_template.xlsx
```

This creates an Excel file with:
- One sheet per database table
- Column headers matching database column names
- Empty rows ready for data entry

### 2. Process Excel via Lambda (AWS)

1. Fill in data in the Excel template
2. Upload Excel file to S3 bucket
3. Lambda automatically processes the file and inserts data into PostgreSQL
4. Reports are generated and uploaded to S3

## Project Structure

```
.
├── scripts/
│   └── generate_excel_from_models.py  # Generate Excel templates (LOCAL USE)
├── lambda_function.py                  # AWS Lambda handler (PRODUCTION)
├── etl/
│   ├── models.py                       # SQLAlchemy models (source of truth)
│   ├── run_etl.py                      # ETL processing logic
│   ├── config/
│   │   └── mappings.yaml               # Excel column mappings & load order
│   └── ...
└── EXCEL_GENERATION_README.md          # Detailed documentation
```

## Key Files

### For Local Development
- **`scripts/generate_excel_from_models.py`** - Generate Excel templates from models
- **`etl/models.py`** - SQLAlchemy models (database schema)

### For Lambda/Production
- **`lambda_function.py`** - AWS Lambda handler
- **`etl/run_etl.py`** - ETL processing engine
- **`etl/config/mappings.yaml`** - Excel column mappings and load order

## Why mappings.yaml?

The `mappings.yaml` file is required for Lambda because:

1. **Column Name Mapping**: Excel files may have different column names than database
   - Maps Excel columns → Database columns via `column_renames`
2. **Load Order**: Defines processing order (important for foreign keys)
3. **Data Type Handling**: Specifies Excel → Database type conversions

See [EXCEL_GENERATION_README.md](EXCEL_GENERATION_README.md) for detailed explanation.

## Local Testing

Test ETL processing locally before uploading:

```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel your_file.xlsx \
    --category masters
```

## Requirements

```bash
pip install -r requirements.txt
```

## Documentation

- **[EXCEL_GENERATION_README.md](EXCEL_GENERATION_README.md)** - Detailed guide on Excel generation and Lambda processing
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Database setup instructions
- **[PRODUCTION_COMMANDS.md](PRODUCTION_COMMANDS.md)** - Production ETL commands

## Workflow

```
1. Generate Excel Template (Local)
   python scripts/generate_excel_from_models.py
   
2. Fill in data in Excel
   
3. Upload Excel to S3
   
4. Lambda processes automatically
   - Reads Excel
   - Maps columns using mappings.yaml
   - Validates using models.py
   - Inserts into PostgreSQL
   - Generates reports
```
