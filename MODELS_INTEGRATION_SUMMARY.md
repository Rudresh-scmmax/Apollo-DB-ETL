# Models.py Integration - Complete Summary

## ✅ What I've Done

I've integrated your SQLAlchemy `models.py` directly into the ETL system! Now you can use models.py as the single source of truth for database schema.

## 🎯 Key Benefits

1. **No More Manual Sync**: When you update models.py, ETL automatically picks up changes
2. **All Tables Included**: All 54+ tables from your models are automatically available
3. **Type Safety**: Data types are automatically extracted from SQLAlchemy model definitions
4. **Less Maintenance**: No need to manually update YAML files when schema changes

## 📁 New Files Created

1. **`etl/models_utils.py`** - Utilities to extract schema info from SQLAlchemy models
2. **`etl/models_loader.py`** - Loads models module and generates ETL configuration
3. **`generate_config_from_models.py`** - Script to auto-generate YAML from models.py
4. **`USING_MODELS_PY.md`** - Complete usage guide

## 🔧 Updated Files

1. **`etl/db.py`** - Now accepts `models_module` parameter for primary keys and columns
2. **`etl/run_etl.py`** - Added `--models-path` argument to use models directly

## 🚀 How to Use

### Quick Start

```bash
# Use models.py directly
python -m etl.run_etl \
    --models-path path/to/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "data.xlsx" \
    --category masters
```

### Generate YAML from Models (Optional)

If you want to see what the YAML would look like, or generate a starting point:

```bash
python generate_config_from_models.py \
    --models-path path/to/models.py \
    --output-dir etl/config
```

This will generate:
- `tables.yaml` - Primary keys for all tables
- `mappings.yaml` - Table configurations with data types

## 🔄 Hybrid Approach

The ETL uses a **hybrid approach**:

| Information | Source | Why |
|------------|--------|-----|
| Primary Keys | `models.py` | Auto-detected from models |
| Column Types | `models.py` | Auto-detected from SQLAlchemy types |
| Table Structure | `models.py` | Auto-detected from models |
| Excel Column Mappings | `mappings.yaml` | Excel-specific, varies by file |
| Load Order | `mappings.yaml` | Business logic, not schema |

## 📊 What Gets Auto-Detected

From your `models.py`, the ETL automatically extracts:

✅ **Primary Keys** - From `__table__.primary_key`  
✅ **Column Names** - From `__table__.columns`  
✅ **Data Types** - Mapped from SQLAlchemy types:
   - `Integer` → `int`
   - `Numeric` → `float`  
   - `Date`/`DateTime` → `date`
   - `Boolean` → `bool`
   - `JSONB` → `dict`
   - `String`/`Text` → `str`
✅ **Foreign Keys** - From `__table__.foreign_keys`

## 🎨 Example Workflow

### Before (YAML-only):
1. Update database schema
2. Update `Create-APOLLO-SQL.sql`
3. Update `etl/config/tables.yaml` (primary keys)
4. Update `etl/config/mappings.yaml` (types, columns)
5. Test ETL

### After (Using models.py):
1. Update database schema
2. Update `models.py` (via sqlacodegen or manually)
3. Run ETL with `--models-path`
4. **Done!** ✅

## 🔍 Current Status

### ✅ Fully Integrated
- Primary key detection from models
- Column type detection from models
- Table structure from models
- Backward compatible with YAML

### ⚠️ Still Need YAML For
- Excel column name mappings (`column_renames`)
- Load order (`load_order` section)
- Table-specific transformations (if any)

## 📝 Next Steps

1. **Test with your models.py**:
   ```bash
   python -m etl.run_etl \
       --models-path path/to/your/models.py \
       --mappings etl/config/mappings.yaml \
       --excel "test_data.xlsx" \
       --category masters \
       --dry-run
   ```

2. **Generate initial YAML** (optional):
   ```bash
   python generate_config_from_models.py \
       --models-path path/to/your/models.py
   ```

3. **Update mappings.yaml**:
   - Keep your existing `load_order`
   - Keep your existing `column_renames` for Excel mappings
   - The ETL will use models for everything else automatically

## 🎉 Result

You now have:
- ✅ All 54+ tables from models.py automatically available
- ✅ Schema always in sync with database
- ✅ No manual YAML updates needed for schema changes
- ✅ Backward compatible - existing YAML still works

## 💡 Pro Tip

You can save your models.py in the project and reference it:

```bash
# Save models.py to project root
cp path/to/models.py ./models.py

# Use it in ETL
python -m etl.run_etl \
    --models-path ./models.py \
    --mappings etl/config/mappings.yaml \
    --excel "data.xlsx"
```

The ETL will automatically:
- Extract all tables
- Get primary keys
- Get column types
- Use YAML only for Excel-specific mappings

**This is exactly what you asked for - using models.py directly!** 🎯

