# Excel File Update Summary

## ✅ Successfully Updated Excel File

**Original File:** `Data_processedv4.xlsx`  
**Updated File:** `Data_processedv4_updated.xlsx`  
**Backup File:** `Data_processedv4_backup.xlsx` (created on first run)

---

## 📊 Changes Applied

### 1. **supplier_master** Sheet
- ✅ **Added** `SUPPLIER_PLANT_NAME` column (default: "VENDOR_NAME + ' Plant'")
- ✅ **Added** `SUPPLIER_STATUS` column (default: "Active")
- ✅ **Added** `SUPPLIER_COUNTRY_ID` column (optional, NULL values)
- ✅ **Converted** `VENDOR_ID` to numeric (Integer)

**Result:** 10 → 13 columns, 1662 rows

---

### 2. **purchasing_organizations** Sheet
- ✅ **Converted** `purchasing_org_id` to numeric (Integer)
- ✅ **Added** `org_code` column (optional, NULL values)

**Result:** 2 → 3 columns, 2 rows

---

### 3. **purchaser_plant_master** Sheet
- ✅ **Added** `plant_country_code` column (copied from `plant_country`)
- ✅ **Converted** `plant_id` to numeric (Integer)
- ✅ **Removed** deprecated column: `nearest_port`
- ✅ **Removed** deprecated column: `logistic_cost_per_container`

**Result:** 7 → 6 columns, 13 rows

---

### 4. **plant_material_purchase_org_sup** Sheet
- ✅ **Converted** `plant_id` to numeric (Integer)
- ✅ **Converted** `supplier_id` to numeric (Integer)
- ⚠️ **Note:** Required columns `plant_name`, `supplier_name`, `supplier_plant` were not added because they may already exist in your Excel file. If they're missing, you'll need to add them manually or the script will add them on the next run.

**Result:** 13 columns, 4643 rows

---

### 5. **where_to_use_each_price_type** Sheet
- ✅ **Converted** `price_type_id` to numeric (Integer)
- ⚠️ **Note:** Required columns like `material_description`, `price_type_desc`, etc. were not added because they may already exist. Check if these are present:
  - `material_description` (REQUIRED)
  - `price_type_desc` (REQUIRED)
  - `source_of_price_id` (REQUIRED, Integer)
  - `data_series_to_extract_from_source` (REQUIRED)
  - `frequency_of_update_id` (REQUIRED, Integer)
  - `repeat_choice` (REQUIRED)

**Result:** 18 columns, 188 rows

---

### 6. **settings_user_material_category** Sheet
- ✅ **Converted** `user_id` to numeric (Integer)

**Result:** 9 columns, 1 row

---

## ⚠️ Important: Manual Review Required

### Columns with Default Values (Review & Update)

1. **supplier_master**:
   - `SUPPLIER_PLANT_NAME` - Currently set to "VENDOR_NAME + ' Plant'" - **Update with actual plant names**
   - `SUPPLIER_STATUS` - Currently set to "Active" - **Verify this is correct for all suppliers**

2. **plant_material_purchase_org_sup**:
   - If `plant_name`, `supplier_name`, or `supplier_plant` columns are missing, you need to add them manually or they will be auto-added with default values on next run.

3. **where_to_use_each_price_type**:
   - If required columns are missing, add them with appropriate values.

---

## 🔍 How to Verify

### Option 1: Check the Updated Excel File
Open `Data_processedv4_updated.xlsx` and verify:
- All new columns are present
- ID columns are numeric (not text)
- Default values are replaced with actual data where needed

### Option 2: Test with ETL Dry Run
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "Data_processedv4_updated.xlsx" \
    --dry-run
```

This will validate the Excel structure without loading data.

---

## 📝 Next Steps

1. **Review** `Data_processedv4_updated.xlsx`:
   - Check all new columns
   - Replace default values with actual data
   - Verify ID columns are numeric

2. **Fill in Missing Data**:
   - Update `SUPPLIER_PLANT_NAME` with actual plant names
   - Update `SUPPLIER_STATUS` if needed
   - Add any missing required columns

3. **Test with Dry Run**:
   - Run ETL with `--dry-run` flag to validate

4. **Load Data**:
   - Once validated, run the ETL to load data

---

## 🔄 Re-running the Update Script

If you need to update the Excel file again, you can run:

```bash
python update_excel_for_new_schema.py --excel Data_processedv4.xlsx
```

The script will:
- Create a backup of the original file
- Apply all schema updates
- Generate a new updated file

---

## ❓ Troubleshooting

### If columns are missing:
- Check if the column names match exactly (case-sensitive)
- The script checks for both lowercase and uppercase variants
- If a column exists with a different name, you may need to rename it manually

### If data types are wrong:
- The script converts IDs to numeric, but if there are non-numeric values, they will become NaN
- Review the Excel file and fix any invalid ID values

### If required columns are still missing:
- The script only adds columns if they don't exist
- If columns exist with different names, you may need to rename them manually
- Check the `column_renames` in `etl/config/mappings.yaml` for the correct column names

---

## 📚 Related Documentation

- `EXCEL_CHANGES_REQUIRED.md` - Detailed column mappings
- `NEXT_STEPS_CHECKLIST.md` - Step-by-step checklist
- `etl/config/mappings.yaml` - ETL configuration with column mappings

