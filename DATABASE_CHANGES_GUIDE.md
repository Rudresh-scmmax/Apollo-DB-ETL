# Guide: Updating ETL Project After Database Table Changes

When you alter database tables, you need to update the following files in this ETL project:

## 1. **`Create-APOLLO-SQL.sql`** (Database Schema Definition)
**Location:** Root directory

**What to update:**
- Table structure (CREATE TABLE statements)
- Column definitions (data types, NULL/NOT NULL constraints)
- Primary key constraints
- Foreign key constraints
- Any new tables or dropped tables

**Why:** This is the source of truth for the database schema. The ETL uses this to create/validate the database structure.

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
- Usually no changes needed - it reads from `Create-APOLLO-SQL.sql`
- If you change the schema file path or validation logic, update here

---

## Quick Checklist When Altering Tables

When you alter a database table, check:

- [ ] **Table structure changed?** → Update `Create-APOLLO-SQL.sql`
- [ ] **Primary key changed?** → Update `etl/config/tables.yaml`
- [ ] **Columns added/removed/renamed?** → Update `etl/config/mappings.yaml`:
  - [ ] `column_renames` section
  - [ ] `dtypes` section
- [ ] **Foreign keys changed?** → Update `etl/load.py` → `fk_constraints`
- [ ] **New table added?** → Add to:
  - [ ] `Create-APOLLO-SQL.sql`
  - [ ] `etl/config/tables.yaml`
  - [ ] `etl/config/mappings.yaml` → `load_order` and `tables` sections
- [ ] **Table removed?** → Remove from all above files
- [ ] **Special transformations needed?** → Update `etl/transform.py` and `etl/run_etl.py`
- [ ] **FK violation handling changed?** → Update `etl/run_etl.py` → `allow_fk` list

---

## Common Scenarios

### Scenario 1: Adding a New Column
1. Update `Create-APOLLO-SQL.sql` - Add column to CREATE TABLE
2. Update `etl/config/mappings.yaml`:
   - Add to `column_renames` (if Excel column name differs)
   - Add to `dtypes`

### Scenario 2: Renaming a Column
1. Update `Create-APOLLO-SQL.sql` - Rename column in CREATE TABLE
2. Update `etl/config/mappings.yaml` - Update `column_renames` mapping
3. Update `etl/config/tables.yaml` - If it's a primary key, update the key name

### Scenario 3: Changing Data Type
1. Update `Create-APOLLO-SQL.sql` - Change column data type
2. Update `etl/config/mappings.yaml` - Update `dtypes` section

### Scenario 4: Adding Foreign Key
1. Update `Create-APOLLO-SQL.sql` - Add FOREIGN KEY constraint
2. Update `etl/load.py` - Add to `fk_constraints` dictionary

### Scenario 5: Changing Primary Key
1. Update `Create-APOLLO-SQL.sql` - Change PRIMARY KEY constraint
2. Update `etl/config/tables.yaml` - Update `primary_key` array
3. Update `etl/config/mappings.yaml` - Ensure `column_renames` and `dtypes` reflect the change

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

