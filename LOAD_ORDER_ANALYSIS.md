# Load Order Analysis and Fixes

## Current Issues

### 1. **location_master** - 212 records rejected
- **Problem:** FK constraint violation for `location_type_id`
- **Root Cause:** Even though `location_type_master` loaded successfully (4 records) and Excel data matches, database INSERT is failing
- **Excel Data Check:**
  - `location_type_master` has IDs: [1, 2, 3, 4] ✓
  - `location_master` uses: [1, 2, 3, 4] ✓ (all match!)
- **Possible Causes:**
  - Database FK constraint enforcement at INSERT time
  - Transaction/commit timing issues
  - Data type mismatch

### 2. **supplier_master** - 1,662 records rejected
- **Problem:** FK constraint violation for `supplier_country_id`
- **FK Constraint:** `supplier_country_id` → `location_master.location_id`
- **Excel Data Check:**
  - `location_master` has location_ids: [1, 2, 3, 4, 5, ..., 212, ...]
  - `supplier_master` has country_ids: [1, 2, 4, 9, 27]
  - **All supplier country_ids exist in location_master** ✓
- **Root Cause:** `location_master` failed to load, so `supplier_master` can't reference it

## Load Order Analysis

Current order in `mappings.yaml`:
1. `location_type_master` (line 6) ✓
2. `location_master` (line 7) ✓ (depends on location_type_master)
3. `supplier_master` (line 8) ✓ (depends on location_master)

**Order is correct!** The issue is that `location_master` is failing at database INSERT time even though FK validation is skipped.

## Root Cause

The FK validation skip works for pre-filtering, but when data tries to INSERT into the database, PostgreSQL enforces FK constraints. If the referenced data isn't committed yet or there's a transaction issue, it fails.

## Solution

Since all the Excel data matches correctly, the issue is likely:
1. **Transaction timing** - Need to ensure tables commit before dependent tables try to insert
2. **FK constraint at database level** - Database is enforcing constraints even though we skip pre-filtering

The real fix needed: Ensure that when master tables skip FK validation, they can still insert successfully even if referenced master tables are in the same transaction.

However, since the Excel data is correct, let me verify if there's a column mapping issue or if the database actually has the referenced data.

