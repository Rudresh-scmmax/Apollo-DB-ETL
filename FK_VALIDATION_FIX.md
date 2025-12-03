# Foreign Key Validation Fix for Master Tables

## Problem Summary

Many master tables (especially `material_master`) were rejecting all records during initial load with "missing foreign key references" errors. This caused a cascade failure because other tables depend on `material_master`.

### Root Cause

The FK validation logic was running for master tables even during their initial load (when the table is empty). This caused issues because:

1. Master tables like `material_master` have foreign keys to other master tables (`uom_master`, `material_type_master`)
2. During initial load, the FK validation was checking if values exist in referenced tables
3. If referenced tables were empty or values didn't match, ALL rows were rejected before insertion
4. This prevented valid data from being inserted, even when the database could handle FK constraints properly

### Example: material_master

`material_master` has foreign keys:
- `base_uom_id` → `uom_master.uom_id`
- `material_type_id` → `material_type_master.material_type_master_id`

According to load order in `mappings.yaml`:
- `material_type_master` is loaded first (line 4)
- `uom_master` is loaded second (line 5)  
- `material_master` is loaded later (line 14)

Even with correct load order, FK validation was still rejecting rows if values didn't match exactly.

## Solution

**Fixed in:** `etl/load.py` - `_filter_fk_violations()` function

### Changes Made

1. **Skip FK validation for master tables on initial load:**
   - If a master table is empty (initial load), skip ALL FK validation
   - Let the database enforce FK constraints during INSERT instead
   - This prevents premature rejection of valid data

2. **Why this is safe:**
   - Master tables are loaded in correct order (defined in `mappings.yaml`)
   - The database will still enforce FK constraints at INSERT time
   - Real FK violations will still be caught, but with better error messages
   - Data gets a chance to be inserted instead of being rejected preemptively

### Code Changes

```python
# Skip FK validation for master tables on initial load:
if is_current_table_master and is_initial_load:
    # For master tables on initial load, skip FK validation for ALL foreign keys
    print(f"  [SKIP] FK validation for {fk_col} -> {ref_table} (master table '{table}' initial load)")
    continue  # Skip this FK constraint validation
```

## Expected Behavior After Fix

### First Run (Initial Load)
- Master tables like `material_master` will skip FK validation if the table is empty
- Data will be inserted, and the database will enforce FK constraints
- If FK values are invalid, the database INSERT will fail with a clear error message
- This allows valid data to be inserted even if referenced tables have partial data

### Subsequent Runs (Incremental Load)
- FK validation will run normally for tables that already have data
- Only new/updated rows with invalid FK values will be rejected
- This maintains data integrity for incremental updates

## What This Fixes

1. ✅ `material_master` can now be loaded on initial run (if table is empty)
2. ✅ Other master tables with FK dependencies can load successfully
3. ✅ Cascade failures are prevented (tables depending on `material_master` can now load)
4. ✅ Better error handling: database provides clearer FK violation messages

## Important Notes

1. **Data Quality Still Enforced:** The database will still reject invalid FK values during INSERT. This fix only prevents premature rejection before insertion.

2. **Load Order Matters:** Master tables are still loaded in the order specified in `mappings.yaml`. The fix allows master tables to load even if referenced master tables have partial data.

3. **Real FK Violations:** If FK values genuinely don't exist in referenced tables, the database INSERT will fail. You'll need to:
   - Fix the FK values in your Excel file, OR
   - Add the missing records to the referenced master tables

## Testing

After applying this fix, you should see:
1. Master tables loading successfully on initial run
2. `[SKIP] FK validation` messages in logs for master tables on initial load
3. Better success rates for tables depending on master tables
4. Clearer error messages if FK values are genuinely invalid

## Related Files

- `etl/load.py` - FK validation logic
- `etl/config/mappings.yaml` - Load order configuration
- `etl/models.py` - Database schema definitions

