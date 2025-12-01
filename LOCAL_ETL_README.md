# Running ETL Locally

This guide explains how to run the ETL locally using `output.xlsx` and optionally `db_query.py` for database operations.

## Prerequisites

1. **Python environment**: Ensure you have a virtual environment activated with all dependencies installed
2. **Database credentials**: Set in `.env` file or environment variables
3. **output.xlsx**: The Excel file to process (should be in project root)
4. **AWS credentials** (if using `db_query.py`): Configured for Lambda invocation

## Setup

### 1. Environment Variables

Create or update your `.env` file with:

```bash
# Required: Direct database connection (always needed for writes/transactions)
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=apollo

# Database connection method
# Default: USE_DB_QUERY_LAMBDA=true (uses Lambda function - required for private VPC)
# Set to 'false' to use direct connection (requires DB credentials below)
USE_DB_QUERY_LAMBDA=true

# Lambda function name defaults to 'client1-private_db_query'
# Override with: DB_QUERY_LAMBDA_FUNCTION=your-lambda-function-name

# Direct connection credentials (only needed if USE_DB_QUERY_LAMBDA=false)
# DB_USER=your_db_user
# DB_PASS=your_db_password
# DB_HOST=your_db_host
```

### 2. Verify Files

Ensure these files exist:
- `output.xlsx` in project root
- `etl/models.py` exists
- `db_query.py` exists (if using Lambda)

## Running the ETL

### Basic Usage (Direct DB Connection)

```bash
python run_etl_local.py
```

This will:
- Use `output.xlsx` from project root
- Connect directly to database
- Create schema if needed
- Run incremental ETL
- Save reports to `reports/` directory

### Using db_query.py Lambda Function

1. Set environment variable:
   ```bash
   export USE_DB_QUERY_LAMBDA=true
   export DB_QUERY_LAMBDA_FUNCTION=your-lambda-function-name
   ```

2. Ensure AWS credentials are configured:
   ```bash
   aws configure
   ```

3. Run:
   ```bash
   python run_etl_local.py
   ```

**Note**: Even with `db_query.py`, a direct database connection is still required for:
- Writes (INSERT/UPDATE)
- Transactions (BEGIN/COMMIT)
- Staging table operations
- Schema creation

The Lambda function is only used for read-only queries when enabled.

## Command Line Options

The script uses these default arguments:
- `--mode incremental`: Updates existing data
- `--excel output.xlsx`: Uses output.xlsx from project root
- `--reports-dir reports/`: Saves reports to reports directory
- `--models-path etl/models.py`: Uses models.py for schema
- `--create-schema`: Creates schema if it doesn't exist

You can modify `run_etl_local.py` to change these defaults.

## Output

After running, you'll find:
- **Reports**: `reports/YYYY-MM-DD_HHMMSS/summary.html`
- **Rejected rows**: `reports/YYYY-MM-DD_HHMMSS/rejected_*.csv`
- **Console output**: Summary of loaded/updated/rejected rows

## Troubleshooting

### "output.xlsx not found"
- Ensure `output.xlsx` is in the project root directory
- Check the file path in the error message

### "Missing DB_USER, DB_PASS, or DB_HOST"
- Set these in your `.env` file
- Or export as environment variables

### "Lambda function error"
- Verify `DB_QUERY_LAMBDA_FUNCTION` is set correctly
- Check AWS credentials: `aws sts get-caller-identity`
- Verify Lambda function exists and has correct permissions

### "db_query.py not found"
- The script will fall back to direct connection
- This is fine - direct connection works for all operations

## Notes

- The ETL processes all tables defined in `etl/config/mappings.yaml`
- FK violations are automatically filtered and reported
- The ETL never fails completely - it processes all valid data and reports errors
- Sheet name matching is case-insensitive and handles variations

