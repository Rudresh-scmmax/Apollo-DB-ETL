# Excel File Changes Required

## Summary

Based on the database schema changes, here's what you need to update in your Excel files:

## 🔴 Critical Changes (Must Update Excel)

### 1. **supplier_master** Sheet

**New Required Columns** (MUST be in Excel):
- ✅ `supplier_plant_name` - **REQUIRED** (String)
- ✅ `supplier_status` - **REQUIRED** (String)

**Column Name Changes:**
- `supplier_id` - Now must be **Integer** (was String)
- `base_currency_accounting` → Now maps to `base_currency_id` (Integer, FK to currency_master)
- `COUNTRY` → Maps to `supplier_country_name` (optional)
- Add `SUPPLIER_COUNTRY_ID` → Maps to `supplier_country_id` (Integer, FK to location_master)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
VENDOR_ID            →  supplier_id (INTEGER - must be numeric)
VENDOR_NAME          →  supplier_name
SUPPLIER_PLANT_NAME  →  supplier_plant_name (NEW - REQUIRED)
SUPPLIER_STATUS      →  supplier_status (NEW - REQUIRED)
COUNTRY              →  supplier_country_name
SUPPLIER_COUNTRY_ID  →  supplier_country_id (NEW - Integer)
PAYMENT_CURRENCY_CODE → base_currency_id (NEW - Integer, not String)
BASE_CURRENCY_ID     →  base_currency_id (Alternative column name)
STATE                →  relevant_country_region
NAME                 →  user_defined_supplier_desc
PARTY_NUMBER         →  supplier_duns
```

---

### 2. **purchasing_organizations** Sheet

**Column Changes:**
- `purchasing_org_id` - Now must be **Integer** (was String)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
purchasing_org_id    →  purchasing_org_id (INTEGER - must be numeric)
purchasing_org_desc  →  purchasing_org_desc
org_code             →  org_code (NEW - optional)
```

---

### 3. **purchaser_plant_master** Sheet

**Column Name Changes:**
- `plant_id` - Now must be **Integer** (was String)
- `plant_country` → `plant_country_code` (column renamed in database)

**Removed Columns** (Remove from Excel if present):
- ❌ `nearest_port` - No longer in database
- ❌ `logistic_cost_per_container` - No longer in database

**Column Type Changes:**
- `special_economic_zone` - Now **String** (was Boolean)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
plant_id             →  plant_id (INTEGER - must be numeric)
plant_name           →  plant_name
plant_country        →  plant_country_code (renamed)
PLANT_COUNTRY_CODE   →  plant_country_code (alternative)
base_currency_accounting → base_currency_accounting
special_economic_zone → special_economic_zone (String: "true"/"false" or "Y"/"N")
```

---

### 4. **plant_material_purchase_org_sup** Sheet

**New Required Columns** (MUST be in Excel):
- ✅ `plant_name` - **REQUIRED** (String)
- ✅ `supplier_name` - **REQUIRED** (String)
- ✅ `supplier_plant` - **REQUIRED** (String)

**Column Name Changes:**
- `plant_id` - Now must be **Integer** (was String)
- `supplier_id` - Now must be **Integer** (was String)
- `User_ID` → `user_id` (lowercase, optional Integer)
- `User_Purchase_Org_ID` → `user_purchase_org_id` (lowercase, optional Integer)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
porg_plant_material_id → porg_plant_material_id
plant_id             →  plant_id (INTEGER - must be numeric)
PLANT_ID             →  plant_id (alternative)
plant_name           →  plant_name (NEW - REQUIRED)
PLANT_NAME           →  plant_name (alternative)
material_id          →  material_id
material_name        →  material_name (NEW - optional)
MATERIAL_NAME        →  material_name (alternative)
purchasing_org_id    →  purchasing_org_id (String - unchanged)
user_id              →  user_id (NEW - lowercase, Integer)
User_ID              →  user_id (old name, still works)
supplier_id          →  supplier_id (INTEGER - must be numeric)
SUPPLIER_ID          →  supplier_id (alternative)
supplier_name        →  supplier_name (NEW - REQUIRED)
SUPPLIER_NAME        →  supplier_name (alternative)
supplier_plant       →  supplier_plant (NEW - REQUIRED)
SUPPLIER_PLANT       →  supplier_plant (alternative)
valid_from           →  valid_from
valid_to             →  valid_to
user_purchase_org_id →  user_purchase_org_id (NEW - lowercase, Integer)
User_Purchase_Org_ID →  user_purchase_org_id (old name, still works)
```

---

### 5. **where_to_use_each_price_type** Sheet

**New Required Columns:**
- ✅ `material_description` - **REQUIRED**
- ✅ `price_type_desc` - **REQUIRED**
- ✅ `source_of_price_id` - **REQUIRED** (Integer)
- ✅ `data_series_to_extract_from_source` - **REQUIRED**
- ✅ `frequency_of_update_id` - **REQUIRED** (Integer)
- ✅ `repeat_choice` - **REQUIRED**

**Column Type Changes:**
- `price_type_id` - Now **Integer** (was String)
- `use_in_cost_sheet` - Now **String** (was Boolean) - Use "true"/"false" or "Y"/"N"
- `use_in_price_benchmarking` - Now **String** (was Boolean)
- `use_in_spend_analytics` - Now **String** (was Boolean)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
porg_material_price_type_id → porg_material_price_type_id
material_id          →  material_id
material_description →  material_description (NEW - REQUIRED)
purchasing_org_id    →  purchasing_org_id
price_type_id        →  price_type_id (INTEGER - must be numeric)
price_type_desc      →  price_type_desc (NEW - REQUIRED)
source_of_price_id   →  source_of_price_id (NEW - REQUIRED, Integer)
data_series_to_extract_from_source → data_series_to_extract_from_source (NEW - REQUIRED)
frequency_of_update_id → frequency_of_update_id (NEW - REQUIRED, Integer)
repeat_choice        →  repeat_choice (NEW - REQUIRED)
data_series_pricing_market → data_series_pricing_market (NEW - optional)
data_series_incoterm → data_series_incoterm (NEW - optional)
data_series_currency → data_series_currency (NEW - optional)
data_series_uom      →  data_series_uom (NEW - optional)
use_in_cost_sheet    →  use_in_cost_sheet (String: "true"/"false")
use_in_price_benchmarking → use_in_price_benchmarking (String)
use_in_spend_analytics → use_in_spend_analytics (String)
last_updated_on      →  last_updated_on (NEW - optional)
```

---

### 6. **settings_user_material_category** Sheet

**Column Type Changes:**
- `user_id` - Now **Integer** (was String)

**Excel Column Mapping:**
```
Excel Column          →  Database Column
─────────────────────────────────────────
user_material_category_id → user_material_category_id
user_id              →  user_id (INTEGER - must be numeric)
... (other columns unchanged)
```

---

## 📋 Quick Checklist

### For Each Excel Sheet, Check:

- [ ] **supplier_master**: 
  - [ ] Add `supplier_plant_name` column (REQUIRED)
  - [ ] Add `supplier_status` column (REQUIRED)
  - [ ] Convert `VENDOR_ID` to Integer (numeric values only)
  - [ ] Update `PAYMENT_CURRENCY_CODE` to map to `base_currency_id` (Integer)

- [ ] **purchasing_organizations**:
  - [ ] Convert `purchasing_org_id` to Integer (numeric values only)
  - [ ] Add `org_code` column (optional)

- [ ] **purchaser_plant_master**:
  - [ ] Convert `plant_id` to Integer (numeric values only)
  - [ ] Rename `plant_country` → `plant_country_code` (or add both)
  - [ ] Change `special_economic_zone` to String format ("true"/"false")
  - [ ] Remove `nearest_port` if present
  - [ ] Remove `logistic_cost_per_container` if present

- [ ] **plant_material_purchase_org_sup**:
  - [ ] Convert `plant_id` to Integer
  - [ ] Convert `supplier_id` to Integer
  - [ ] Add `plant_name` column (REQUIRED)
  - [ ] Add `supplier_name` column (REQUIRED)
  - [ ] Add `supplier_plant` column (REQUIRED)
  - [ ] Update `User_ID` → `user_id` (lowercase)
  - [ ] Update `User_Purchase_Org_ID` → `user_purchase_org_id` (lowercase)

- [ ] **where_to_use_each_price_type**:
  - [ ] Convert `price_type_id` to Integer
  - [ ] Add all new required columns
  - [ ] Change boolean columns to String format

---

## 🔍 How to Verify Your Excel Files

### Option 1: Test with Dry Run
```bash
python -m etl.run_etl \
    --models-path etl/models.py \
    --mappings etl/config/mappings.yaml \
    --excel "your_file.xlsx" \
    --dry-run
```

This will validate your Excel structure without loading data.

### Option 2: Check Column Mappings

The ETL will automatically:
- ✅ Map Excel columns to database columns using `column_renames`
- ✅ Convert data types based on `dtypes` (now from models.py)
- ✅ Validate required fields

If columns are missing, you'll see errors in the report.

---

## 💡 Tips

1. **Integer IDs**: Make sure ID columns contain only numeric values (no text, no spaces)

2. **Required Fields**: The ETL will reject rows missing required fields. Check the rejected CSV files for details.

3. **Column Names**: Excel column names are case-sensitive in the mappings. Use exact names as shown in `column_renames`.

4. **Boolean to String**: For fields that changed from Boolean to String, use:
   - "true"/"false" or "Y"/"N" or "1"/"0"

5. **New Tables**: For new tables, you may need to add Excel sheets with the correct column names.

---

## 🚨 Most Critical Changes

**Priority 1** (Will cause ETL failures):
1. ✅ `supplier_master.supplier_plant_name` - Add this column
2. ✅ `supplier_master.supplier_status` - Add this column
3. ✅ `plant_material_purchase_org_sup.plant_name` - Add this column
4. ✅ `plant_material_purchase_org_sup.supplier_name` - Add this column
5. ✅ `plant_material_purchase_org_sup.supplier_plant` - Add this column
6. ✅ Convert all ID columns from String to Integer format

**Priority 2** (May cause data issues):
- Update column names (plant_country → plant_country_code)
- Update boolean fields to String format
- Remove deprecated columns

---

## 📝 Next Steps

1. **Update Excel Files** with the changes above
2. **Test with Dry Run** to validate structure
3. **Run ETL** with a small dataset first
4. **Check Reports** for any rejected rows
5. **Fix Issues** based on rejection reasons

The ETL will now automatically use models.py for schema validation, so any mismatches will be caught immediately!

