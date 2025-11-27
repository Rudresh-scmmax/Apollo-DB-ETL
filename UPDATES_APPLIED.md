# ETL Configuration Updates Applied

## Summary
Updated ETL configuration files to match the current database schema based on SQLAlchemy models.

## Files Updated

### 1. `etl/config/mappings.yaml`

#### ✅ **supplier_master**
- **Changed:** `supplier_id` from `str` → `int`
- **Added Required Fields:**
  - `supplier_plant_name` (str, REQUIRED)
  - `supplier_status` (str, REQUIRED)
- **Added Optional Fields:**
  - `supplier_country_id` (int, FK to location_master)
  - `supplier_country_name` (str)
- **Changed:** `base_currency_accounting` → `base_currency_id` (int, FK to currency_master)

#### ✅ **purchasing_organizations**
- **Changed:** `purchasing_org_id` from `str` → `int`
- **Added:** `org_code` (str, optional)

#### ✅ **purchaser_plant_master**
- **Changed:** `plant_id` from `str` → `int`
- **Changed:** `plant_country` → `plant_country_code` (column rename)
- **Changed:** `special_economic_zone` from `bool` → `str`
- **Removed:** `nearest_port` (not in database)
- **Removed:** `logistic_cost_per_container` (not in database)

#### ✅ **plant_material_purchase_org_supplier**
- **Changed:** `plant_id` from `str` → `int`
- **Changed:** `supplier_id` from `str` → `int`
- **Changed:** `User_ID` → `user_id` (lowercase, optional int)
- **Changed:** `User_Purchase_Org_ID` → `user_purchase_org_id` (lowercase, optional int)
- **Added Required Fields:**
  - `plant_name` (str, REQUIRED)
  - `supplier_name` (str, REQUIRED)
  - `supplier_plant` (str, REQUIRED)
- **Added Optional Field:**
  - `material_name` (str)
- **Note:** `purchasing_org_id` remains `str` (String(20) in database)

#### ✅ **where_to_use_each_price_type**
- **Changed:** `price_type_id` from `str` → `int`
- **Changed:** `use_in_cost_sheet` from `bool` → `str`
- **Changed:** `use_in_price_benchmarking` from `bool` → `str`
- **Changed:** `use_in_spend_analytics` from `bool` → `str`
- **Added Required Fields:**
  - `material_description` (str)
  - `price_type_desc` (str)
  - `source_of_price_id` (int)
  - `data_series_to_extract_from_source` (str)
  - `frequency_of_update_id` (int)
  - `repeat_choice` (str)
- **Added Optional Fields:**
  - `data_series_pricing_market` (str)
  - `data_series_incoterm` (str)
  - `data_series_currency` (str)
  - `data_series_uom` (str)
  - `last_updated_on` (date)

#### ✅ **pricing_type_master**
- **Changed:** `source_of_price` from `int` → `str`
- **Changed:** `frequency_of_update` from `int` → `str`

#### ✅ **settings_user_material_category**
- **Changed:** `user_id` from `str` → `int`

#### ✅ **Repeat_Master**
- **Changed:** `repeat_choices` from `str` → `dict` (JSONB in database)

#### ✅ **UoM Master**
- **Changed:** `synonyms` from `str` → `dict` (JSONB in database)

#### ✅ **port_master**
- **Added:** `freight_mode` (str, optional)

### 2. `etl/load.py`

#### ✅ **Updated FK Constraints**
- Updated `fk_constraints` dictionary to reflect new data types
- Added FK constraints for:
  - `supplier_master` → `location_master` and `currency_master`
  - `purchaser_plant_master` → `country_master` and `currency_master`
  - `where_to_use_each_price_type` → multiple reference tables
- Updated comments to note integer type changes

### 3. `etl/transform.py`

#### ✅ **Updated `map_purchasing_org_name_to_id()`**
- Enhanced to handle both integer and string ID formats
- Improved ID matching logic for better compatibility

#### ✅ **Updated `coerce_types_for_table()`**
- Added support for `dict` type (JSONB fields)
- Handles dict, JSON strings, and comma-separated values
- Properly converts to JSON string format for database storage

## Critical Changes Summary

### Data Type Changes (Will cause failures if not updated)
1. ✅ `purchasing_organizations.purchasing_org_id`: `str` → `int`
2. ✅ `supplier_master.supplier_id`: `str` → `int`
3. ✅ `purchaser_plant_master.plant_id`: `str` → `int`
4. ✅ `plant_material_purchase_org_supplier.plant_id`: `str` → `int`
5. ✅ `plant_material_purchase_org_supplier.supplier_id`: `str` → `int`
6. ✅ `settings_user_material_category.user_id`: `str` → `int`
7. ✅ `where_to_use_each_price_type.price_type_id`: `str` → `int`

### Required Fields Added (Must be in Excel)
1. ✅ `supplier_master.supplier_plant_name`
2. ✅ `supplier_master.supplier_status`
3. ✅ `plant_material_purchase_org_supplier.plant_name`
4. ✅ `plant_material_purchase_org_supplier.supplier_name`
5. ✅ `plant_material_purchase_org_supplier.supplier_plant`

### Column Name Changes
1. ✅ `purchaser_plant_master.plant_country` → `plant_country_code`
2. ✅ `plant_material_purchase_org_supplier.User_ID` → `user_id`
3. ✅ `plant_material_purchase_org_supplier.User_Purchase_Org_ID` → `user_purchase_org_id`

## Next Steps

1. **Update Excel Files:**
   - Ensure all new required fields are present
   - Update column names to match new mappings
   - Verify data types match (especially integer IDs)

2. **Test ETL Process:**
   - Run ETL with a small test dataset
   - Verify all tables load correctly
   - Check for any FK violation errors

3. **Verify Data:**
   - Confirm integer IDs are being loaded correctly
   - Check JSON fields (synonyms, repeat_choices) are properly formatted
   - Validate foreign key relationships

## Notes

- The `purchasing_org_id` in `plant_material_purchase_org_supplier` remains `str` (String(20)) even though `purchasing_organizations.purchasing_org_id` is now `int`. This is correct per the database schema.
- JSON fields (`synonyms`, `repeat_choices`) are now stored as JSONB/dict in the database. The ETL will convert comma-separated strings to JSON format automatically.
- Foreign key validation has been updated to handle the new integer types correctly.

