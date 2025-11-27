# Using models.py Directly in ETL

## Overview

You can now use your SQLAlchemy `models.py` file directly as the source of truth for the ETL, eliminating the need to manually sync YAML files with database schema changes.

## Benefits

✅ **Single Source of Truth**: Schema defined once in `models.py`  
✅ **Auto-Sync**: When database changes, models.py changes, ETL automatically picks it up  
✅ **Type Safety**: SQLAlchemy handles type conversions  
✅ **Less Maintenance**: No need to manually sync YAML with database  
✅ **All Tables Included**: Automatically includes all tables from models.py  

## How It Works

The ETL now supports a **hybrid approach**:

1. **Schema Information** (from `models.py`):
   - Primary keys
   - Column names
   - Data types
   - Foreign key relationships

2. **Excel Mappings** (from `mappings.yaml`):
   - Column renames (Excel column → Database column)
   - Load order (which tables to process and in what order)
   - Table-specific transformations

## Usage

### Option 1: Use Models + YAML (Recommended)

```bash
python -m etl.run_etl \
    --models-path path/to/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "data.xlsx"
```

**What happens:**
- Primary keys, column types, and table structure come from `models.py`
- Excel column mappings and load order come from `mappings.yaml`
- Best of both worlds!

### Option 2: Use Models Only (Auto-generate everything)

If you want to use models for everything, you can:

1. Create a minimal `mappings.yaml` with just `load_order`:
```yaml
load_order:
  masters:
    - Currency_Master
    - Material_Type_Master
    # ... etc
  relationship: []
  transactional: []
```

2. Run with models:
```bash
python -m etl.run_etl \
    --models-path path/to/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "data.xlsx"
```

The ETL will:
- Auto-detect all tables from models.py
- Auto-generate data types from model definitions
- Use YAML only for Excel column name mappings (if needed)

### Option 3: Traditional YAML-only (Backward Compatible)

```bash
python -m etl.run_etl \
    --mappings etl/config/mappings.yaml \
    --tables-config etl/config/tables.yaml \
    --excel "data.xlsx"
```

Works exactly as before - no changes needed!

## What Gets Auto-Generated from Models

When you use `--models-path`, the ETL automatically extracts:

1. **Primary Keys**: From `__table_args__` or `__table__.primary_key`
2. **Column Names**: From `__table__.columns`
3. **Data Types**: Mapped from SQLAlchemy types:
   - `Integer` → `int`
   - `Numeric` → `float`
   - `Date`/`DateTime` → `date`
   - `Boolean` → `bool`
   - `JSONB` → `dict`
   - `String`/`Text` → `str`
4. **Foreign Keys**: From `__table__.foreign_keys`

## Example: Adding a New Table

### Before (YAML-only):
1. Add table to `Create-APOLLO-SQL.sql`
2. Add primary key to `etl/config/tables.yaml`
3. Add full configuration to `etl/config/mappings.yaml`
4. Update `load_order` in `mappings.yaml`

### After (Using models.py):
1. Add model class to `models.py`
2. Add to `load_order` in `mappings.yaml` (if needed)
3. Add Excel column mappings (if Excel column names differ)
4. **Done!** Everything else is auto-detected

## Migration Guide

### Step 1: Save your models.py

Save your models.py file somewhere accessible:
```bash
cp path/to/models.py ./models.py
# or
cp path/to/app/db/models/models.py ./models.py
```

### Step 2: Update your mappings.yaml (Optional)

You can keep your existing `mappings.yaml` - it will still work. The ETL will:
- Use models for schema info (primary keys, types)
- Use YAML for Excel mappings (column_renames, load_order)

### Step 3: Run ETL with models

```bash
python -m etl.run_etl \
    --models-path ./models.py \
    --mappings etl/config/mappings.yaml \
    --excel "data.xlsx" \
    --category masters
```

## Files Created

1. **`etl/models_utils.py`**: Utilities to extract info from SQLAlchemy models
2. **`etl/models_loader.py`**: Loads models module and generates ETL config
3. **Updated `etl/db.py`**: Now accepts models_module parameter
4. **Updated `etl/run_etl.py`**: Added `--models-path` argument

## Notes

- **Backward Compatible**: Existing YAML-based workflows still work
- **Hybrid Approach**: Use models for schema, YAML for Excel-specific mappings
- **Auto-Discovery**: All tables in models.py are automatically available
- **Type Safety**: SQLAlchemy types are properly mapped to ETL types

## Troubleshooting

### Models not found?
```bash
# Specify full path
python -m etl.run_etl --models-path /full/path/to/models.py ...
```

### Column type mismatches?
- Check that your Excel data matches the types in models.py
- The ETL will auto-convert based on model definitions

### Missing tables?
- All tables in models.py are automatically available
- Just add them to `load_order` in mappings.yaml if you want to process them

