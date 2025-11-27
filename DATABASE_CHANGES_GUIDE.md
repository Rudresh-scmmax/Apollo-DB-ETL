# Guide: Updating ETL Project After Database Table Changes

When you alter database tables, you need to update the following files in this ETL project:

## 1. **`etl/models.py`** (Database Schema Definition - Source of Truth)
**Location:** `etl/models.py`

**What to update:**
- SQLAlchemy model classes (add/remove/modify)
- Column definitions (data types, nullable constraints)
- Primary key constraints (in `__table_args__` or `mapped_column`)
- Foreign key relationships (using `ForeignKey` or `relationship`)
- Any new tables or dropped tables

**Why:** This is the **single source of truth** for the database schema. The ETL uses this to:
- Create database schema automatically
- Validate table structure
- Extract primary keys and column types
- Generate Excel templates

**Note:** The old `Create-APOLLO-SQL.sql` file has been archived as it was outdated. All schema is now managed through `models.py`.

---

## 2. **`etl/config/tables.yaml`** (Primary Key Definitions)
**Location:** `etl/config/tables.yaml`

**What to update:**
- Add/remove table entries
- Update `primary_key` arrays if primary keys change
- Ensure table names match exactly (case-sensitive)

**Example:**
```yaml
your_table_name:
  primary_key: [column1, column2]  # Update if PK changes
```

**Why:** The ETL uses this to determine which columns are primary keys for upsert operations.

---

## 3. **`etl/config/mappings.yaml`** (Table Mappings & Configuration)
**Location:** `etl/config/mappings.yaml`

**What to update for each affected table:**

### a) **`load_order` section:**
- Add/remove table names from `masters`, `core`, `relationship`, or `transactional` lists
- Ensure table names match Excel sheet names (case-sensitive)

### b) **`tables` section:**
For each table, update:

- **`target_table`**: Target database table name
- **`column_renames`**: Map Excel column names → database column names
  ```yaml
  column_renames:
    excel_column_name: database_column_name
  ```
- **`dtypes`**: Data types for each column (must match database schema)
  ```yaml
  dtypes:
    column_name: int|str|float|date|bool
  ```
- **`incremental.strategy`**: Usually `business_key_upsert` (rarely changes)

**Why:** This file controls:
- Which tables are processed and in what order
- How Excel columns map to database columns
- Data type conversions
- Upsert strategies

---

## 4. **`etl/load.py`** (Foreign Key Constraints)
**Location:** `etl/load.py`

**What to update:**
- **`_filter_fk_violations()` function** (lines 11-56):
  - Update `fk_constraints` dictionary if foreign keys change
  - Add/remove foreign key relationships
  - Format: `('fk_column', 'referenced_table', 'referenced_column')`

**Example:**
```python
fk_constraints = {
    'your_table': [
        ('fk_column', 'referenced_table', 'referenced_column'),
    ]
}
```

**Why:** This prevents foreign key violations during data loading.

---

## 5. **`etl/transform.py`** (Data Transformations)
**Location:** `etl/transform.py`

**What to update if transformations are needed:**

### a) **`auto_generate_missing_keys()` function** (lines 34-61):
- Update `auto_gen_tables` dictionary if tables with auto-generated keys change
- Format: `'table_name': 'primary_key_column'`

### b) **`apply_json_transforms()` function** (lines 87-103):
- Update `json_transforms` dictionary if JSON column transformations are needed
- Format: `'table_name': ['column1', 'column2']`

### c) **Mapping functions:**
- `map_purchasing_org_name_to_id()` - If purchasing_org_id mappings change
- `map_material_type_desc_to_id()` - If material_type_id mappings change
- `map_location_type_desc_to_id()` - If location_type_id mappings change

**Why:** These functions handle special data transformations and lookups.

---

## 6. **`etl/run_etl.py`** (ETL Orchestration)
**Location:** `etl/run_etl.py`

**What to update:**
- **Table-specific transformations** (lines 149-164):
  - If you add/remove tables that need special transformations, update the conditional logic
  - Currently handles: `material_master`, `location_master`, `plant_material_purchase_org_supplier`, `uom_conversion`
  
- **Foreign key violation handling** (line 194):
  - Update the list of tables that allow FK violations: `['plant_material_purchase_org_supplier', 'where_to_use_each_price_type']`
  - Add/remove table names if FK validation behavior changes

**Example:**
```python
# Table-specific transforms
if target_table == 'your_table':
    df = your_custom_transform_function(df, args.excel)

# FK violation handling
allow_fk = target_table in ['table1', 'table2', 'your_table']
```

**Why:** This file orchestrates the ETL process and contains table-specific business logic.

---

## 7. **`etl/schema.py`** (Schema Validation)
**Location:** `etl/schema.py`

**What to update:**
- Usually no changes needed - it reads from `etl/models.py`
- If you change the schema file path or validation logic, update here

---

## Quick Checklist When Altering Tables

When you alter a database table, check:

- [ ] **Table structure changed?** → Update `etl/models.py`
- [ ] **Primary key changed?** → Update `etl/config/tables.yaml`
- [ ] **Columns added/removed/renamed?** → Update `etl/config/mappings.yaml`:
  - [ ] `column_renames` section
  - [ ] `dtypes` section
- [ ] **Foreign keys changed?** → Update `etl/load.py` → `fk_constraints`
- [ ] **New table added?** → Add to:
  - [ ] `etl/models.py`
  - [ ] `etl/config/tables.yaml`
  - [ ] `etl/config/mappings.yaml` → `load_order` and `tables` sections
- [ ] **Table removed?** → Remove from all above files
- [ ] **Special transformations needed?** → Update `etl/transform.py` and `etl/run_etl.py`
- [ ] **FK violation handling changed?** → Update `etl/run_etl.py` → `allow_fk` list

---

## Common Scenarios

### Scenario 1: Adding a New Column
1. Update `etl/models.py` - Add column to the model class
2. Update `etl/config/mappings.yaml`:
   - Add to `column_renames` (if Excel column name differs)
   - Add to `dtypes` (or let it auto-detect from models)

### Scenario 2: Renaming a Column
1. Update `etl/models.py` - Rename column in the model class
2. Update `etl/config/mappings.yaml` - Update `column_renames` mapping
3. If it's a primary key, the change in models.py will be automatically picked up

### Scenario 3: Changing Data Type
1. Update `etl/models.py` - Change column data type in the model
2. Update `etl/config/mappings.yaml` - Update `dtypes` mapping (or let it auto-detect from models)

### Scenario 4: Adding Foreign Key
1. Update `etl/models.py` - Add `ForeignKey` or `relationship` to the model
2. Update `etl/load.py` - Add to `fk_constraints` dictionary (if needed)

### Scenario 5: Changing Primary Key
1. Update `etl/models.py` - Change primary key in `__table_args__` or `mapped_column(primary_key=True)`
2. The change will be automatically detected by the ETL from models.py

### Scenario 6: Adding Table-Specific Transformations
1. Add transformation function to `etl/transform.py`
2. Update `etl/run_etl.py` - Add conditional logic in the table-specific transforms section (lines 149-164)
3. Ensure the transformation is called for the correct `target_table` name

---

## Testing After Changes

After making changes:
1. Test database schema creation: Run schema creation to ensure SQL is valid
2. Test ETL with sample data: Run the ETL process with a small dataset
3. Check logs: Review ETL logs for any errors or warnings
4. Validate data: Verify data is loaded correctly into the database

---

## Notes

- **Case Sensitivity**: Table and column names are case-sensitive in YAML files
- **Excel Sheet Names**: The `load_order` section uses Excel sheet names (may differ from table names)
- **Column Mapping**: Always check both source (Excel) and target (database) column names
- **Data Types**: Ensure Python data types in `mappings.yaml` match PostgreSQL types in SQL file

