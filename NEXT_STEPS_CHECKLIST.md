# Next Steps Checklist

## ✅ What's Already Done

- [x] Updated `etl/config/mappings.yaml` with new schema
- [x] Updated `etl/config/tables.yaml` with primary keys
- [x] Updated `etl/load.py` with foreign key constraints
- [x] Updated `etl/transform.py` for new data types
- [x] Integrated `models.py` support into ETL
- [x] Added all 54+ new tables to configuration

## 🔴 What You Need to Do Next

### 1. Update Your Excel Files (REQUIRED)

**Critical Changes Needed:**

#### **supplier_master** Sheet:
- [ ] **ADD** `supplier_plant_name` column (REQUIRED - cannot be empty)
- [ ] **ADD** `supplier_status` column (REQUIRED - cannot be empty)
- [ ] **CHANGE** `VENDOR_ID` values to **Integer** (must be numeric, not text)
- [ ] **ADD** `SUPPLIER_COUNTRY_ID` column (optional, Integer)
- [ ] **UPDATE** `PAYMENT_CURRENCY_CODE` → Should map to `base_currency_id` (Integer FK)

#### **purchasing_organizations** Sheet:
- [ ] **CHANGE** `purchasing_org_id` values to **Integer** (must be numeric)
- [ ] **ADD** `org_code` column (optional)

#### **purchaser_plant_master** Sheet:
- [ ] **CHANGE** `plant_id` values to **Integer** (must be numeric)
- [ ] **RENAME** `plant_country` column → `plant_country_code` (or add both)
- [ ] **CHANGE** `special_economic_zone` to String format ("true"/"false" or "Y"/"N")
- [ ] **REMOVE** `nearest_port` column (if present)
- [ ] **REMOVE** `logistic_cost_per_container` column (if present)

#### **plant_material_purchase_org_sup** Sheet:
- [ ] **ADD** `plant_name` column (REQUIRED)
- [ ] **ADD** `supplier_name` column (REQUIRED)
- [ ] **ADD** `supplier_plant` column (REQUIRED)
- [ ] **CHANGE** `plant_id` values to **Integer** (must be numeric)
- [ ] **CHANGE** `supplier_id` values to **Integer** (must be numeric)
- [ ] **RENAME** `User_ID` → `user_id` (lowercase, or keep both)
- [ ] **RENAME** `User_Purchase_Org_ID` → `user_purchase_org_id` (lowercase, or keep both)

#### **where_to_use_each_price_type** Sheet:
- [ ] **ADD** `material_description` column (REQUIRED)
- [ ] **ADD** `price_type_desc` column (REQUIRED)
- [ ] **ADD** `source_of_price_id` column (REQUIRED, Integer)
- [ ] **ADD** `data_series_to_extract_from_source` column (REQUIRED)
- [ ] **ADD** `frequency_of_update_id` column (REQUIRED, Integer)
- [ ] **ADD** `repeat_choice` column (REQUIRED)
- [ ] **CHANGE** `price_type_id` values to **Integer** (must be numeric)
- [ ] **CHANGE** boolean columns (`use_in_cost_sheet`, etc.) to String format

#### **settings_user_material_category** Sheet:
- [ ] **CHANGE** `user_id` values to **Integer** (must be numeric)

---

### 2. Test Your Excel Files

**Option A: Dry Run (Recommended First)**
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "your_file.xlsx" \
    --category masters \
    --dry-run
```

This will:
- ✅ Validate Excel structure
- ✅ Check column mappings
- ✅ Verify data types
- ✅ **NO data will be loaded** (safe to test)

**Option B: Test with Small Dataset**
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "test_data.xlsx" \
    --category masters \
    --mode initial
```

---

### 3. Review ETL Reports

After running, check the HTML report in `reports/[timestamp]/summary.html`:
- ✅ See which tables loaded successfully
- ✅ See which rows were rejected and why
- ✅ Get business-friendly error messages

---

## 📊 Summary: Excel Changes Required

### Must Add (New Required Columns):
1. `supplier_master.supplier_plant_name` ⚠️ REQUIRED
2. `supplier_master.supplier_status` ⚠️ REQUIRED
3. `plant_material_purchase_org_sup.plant_name` ⚠️ REQUIRED
4. `plant_material_purchase_org_sup.supplier_name` ⚠️ REQUIRED
5. `plant_material_purchase_org_sup.supplier_plant` ⚠️ REQUIRED
6. `where_to_use_each_price_type.material_description` ⚠️ REQUIRED
7. `where_to_use_each_price_type.price_type_desc` ⚠️ REQUIRED
8. `where_to_use_each_price_type.source_of_price_id` ⚠️ REQUIRED
9. `where_to_use_each_price_type.data_series_to_extract_from_source` ⚠️ REQUIRED
10. `where_to_use_each_price_type.frequency_of_update_id` ⚠️ REQUIRED
11. `where_to_use_each_price_type.repeat_choice` ⚠️ REQUIRED

### Must Convert to Integer (ID Columns):
1. `supplier_master.VENDOR_ID` → Integer
2. `purchasing_organizations.purchasing_org_id` → Integer
3. `purchaser_plant_master.plant_id` → Integer
4. `plant_material_purchase_org_sup.plant_id` → Integer
5. `plant_material_purchase_org_sup.supplier_id` → Integer
6. `where_to_use_each_price_type.price_type_id` → Integer
7. `settings_user_material_category.user_id` → Integer

### Must Rename:
1. `purchaser_plant_master.plant_country` → `plant_country_code`
2. `plant_material_purchase_org_sup.User_ID` → `user_id` (or keep both)
3. `plant_material_purchase_org_sup.User_Purchase_Org_ID` → `user_purchase_org_id` (or keep both)

### Must Remove (If Present):
1. `purchaser_plant_master.nearest_port`
2. `purchaser_plant_master.logistic_cost_per_container`

---

## 🎯 Quick Start Guide

### Step 1: Update Excel Files
Update your Excel files with the changes listed above.

### Step 2: Test with Dry Run
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "your_file.xlsx" \
    --dry-run
```

### Step 3: Check Results
- If dry-run passes → Proceed to load data
- If errors → Fix Excel files based on error messages

### Step 4: Load Data
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "your_file.xlsx" \
    --category masters \
    --mode initial
```

### Step 5: Review Reports
Check `reports/[timestamp]/summary.html` for:
- Successfully loaded tables
- Rejected rows and reasons
- Action items

---

## 💡 Pro Tips

1. **Start Small**: Test with one table first (e.g., `--tables Currency_Master`)

2. **Use Dry Run**: Always test with `--dry-run` first to catch issues

3. **Check Rejected Rows**: The ETL generates CSV files for rejected rows with reasons

4. **Integer IDs**: Make sure ID columns contain only numbers (no text, spaces, or special characters)

5. **Required Fields**: Fill in all required fields - empty cells will cause rejections

6. **Column Names**: Excel column names must match exactly (case-sensitive) what's in `column_renames`

---

## ❓ Do You Need to Change Excel?

**YES** - You need to update your Excel files for:

1. ✅ **New Required Columns** - Add the 11 new required columns listed above
2. ✅ **Data Type Changes** - Convert ID columns from text to numeric (Integer)
3. ✅ **Column Renames** - Update column names to match new database schema
4. ✅ **Remove Deprecated Columns** - Remove columns that no longer exist

**The ETL configuration is ready** - now you just need to update your Excel files to match!

---

## 📚 Reference Documents

- `EXCEL_CHANGES_REQUIRED.md` - Detailed Excel column mappings
- `UPDATES_APPLIED.md` - Summary of all configuration changes
- `USING_MODELS_PY.md` - Guide for using models.py directly

