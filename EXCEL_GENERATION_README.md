# Excel Template Generation

## Overview

This project has **two separate workflows**:

1. **Local Excel Generation** - Create Excel templates from database models
2. **Lambda ETL Processing** - Process uploaded Excel files and insert data into database

---

## 1. Local Excel Generation (For Data Entry)

### Purpose
Generate Excel template files with proper column headers for data entry.

### Script
**`scripts/generate_excel_from_models.py`** - Creates Excel file directly from SQLAlchemy models

### Usage
```bash
# Generate Excel template from models
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

## 2. Lambda ETL Processing (For Data Upload)

### Purpose
Process uploaded Excel files and insert data into PostgreSQL database.

### How It Works
1. User uploads Excel file to S3 bucket
2. Lambda function is triggered
3. Lambda processes Excel and inserts data into database

### Why `mappings.yaml` is Needed

The `mappings.yaml` file is **required for Lambda** because:

1. **Column Name Mapping**: Excel files uploaded by users may have different column names than database columns
   - Example: Excel has `VENDOR_ID` but database has `vendor_id`
   - `column_renames` maps Excel columns → Database columns

2. **Load Order**: Defines which tables to process first (important for foreign key dependencies)
   - Masters → Core → Relationship → Transactional

3. **Data Type Handling**: Specifies how to convert Excel data types to database types

4. **Flexibility**: Allows users to upload Excel files with custom column names without changing code

### Lambda Configuration
The Lambda function (`lambda_function.py`) uses:
- `etl/models.py` - For database schema (primary keys, column types)
- `etl/config/mappings.yaml` - For Excel column mappings and load order

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ LOCAL DEVELOPMENT                                            │
│                                                              │
│  1. Generate Excel Template                                 │
│     python generate_excel_from_models.py                    │
│                                                              │
│  2. Fill in data in Excel                                   │
│                                                              │
│  3. Upload Excel to S3                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ LAMBDA (AWS)                                                 │
│                                                              │
│  1. Excel uploaded to S3 triggers Lambda                    │
│                                                              │
│  2. Lambda reads Excel                                      │
│     - Uses mappings.yaml for column mapping                 │
│     - Uses models.py for schema validation                  │
│                                                              │
│  3. Data inserted into PostgreSQL                           │
│                                                              │
│  4. Reports generated and uploaded to S3                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files

### For Local Excel Generation
- **`scripts/generate_excel_from_models.py`** - Main script to generate Excel from models
- **`etl/models.py`** - SQLAlchemy models (source of truth for schema)

### For Lambda ETL
- **`lambda_function.py`** - AWS Lambda handler
- **`etl/run_etl.py`** - ETL processing logic
- **`etl/config/mappings.yaml`** - Excel column mappings and load order
- **`etl/models.py`** - Database schema validation

---

## Best Practices

1. **Always use `scripts/generate_excel_from_models.py`** to create new Excel templates
   - Ensures column names match database exactly
   - Includes all tables automatically

2. **Keep `mappings.yaml` updated** when Excel column names differ from database
   - Add entries to `column_renames` for any name differences

3. **Test locally before uploading**
   - Use `python -m etl.run_etl` locally to test Excel processing

---

## Troubleshooting

### Excel columns don't match database
- Check `mappings.yaml` → `column_renames` section
- Add mapping: `Excel_Column_Name: database_column_name`

### Missing tables in Excel
- Run `scripts/generate_excel_from_models.py` to regenerate template
- All tables from models.py will be included

### Lambda errors on upload
- Check Lambda logs in CloudWatch
- Verify `mappings.yaml` has correct column mappings
- Ensure Excel sheet names match table names in `load_order`

