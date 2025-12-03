# Report Generation Fixes

## Issues Found and Fixed

### 1. **Duplicate Table Entries**
**Problem:** Tables like `action_plans`, `admin_user`, and `calendar_master` appeared twice in the report.

**Root Cause:** When errors occurred, the code was calling both:
- `reporter.record_error()` - which adds a row
- `reporter.record_table()` - which adds another row

This created duplicate entries for the same table.

**Fix Applied:**
- Removed duplicate `record_table()` calls after `record_error()` in error handling
- Added deduplication logic in `finalize()` method to merge entries with same sheet/table combination
- Deduplication keeps the entry with the most activity (read, inserted, updated, or rejected rows)

### 2. **Empty Rows Showing as Errors**
**Problem:** Tables with 0 records read were showing as ERROR status, cluttering the report.

**Fix Applied:**
- Added logic to skip rows with no activity (0 read, 0 inserted, 0 updated, 0 rejected)
- Only show ERROR status if there's an actual error message in notes
- This cleans up the report by hiding empty/inactive entries

### 3. **Incorrect Totals**
**Problem:** Totals were being calculated from all rows (including duplicates), inflating the numbers.

**Fix Applied:**
- Updated totals calculation to use deduplicated rows only
- Ensures totals match the actual table entries shown

### 4. **Rejection Section Using Duplicates**
**Problem:** The "Why Were Records Rejected?" section was also using duplicate rows.

**Fix Applied:**
- Updated rejection section to use deduplicated rows

## Files Changed

1. **`etl/report.py`**
   - Added deduplication logic in `finalize()` method
   - Updated totals calculation to use deduplicated rows
   - Added logic to skip empty rows
   - Updated rejection section to use deduplicated rows

2. **`etl/run_etl.py`**
   - Removed duplicate `record_table()` calls in error handling
   - Only `record_error()` is called now when errors occur

## Expected Results

After these fixes:
- ✅ No duplicate table entries in reports
- ✅ Cleaner reports (empty rows are hidden)
- ✅ Accurate totals matching displayed entries
- ✅ Single entry per table with correct aggregated data

## Testing

To verify the fixes:
1. Run the ETL again
2. Check the generated report for:
   - No duplicate entries
   - Clean, organized table list
   - Accurate totals
   - Single entry per table

