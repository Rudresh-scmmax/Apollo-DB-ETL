# APOLLO Database Setup Guide

## Overview
The ETL pipeline can now create the complete APOLLO database schema automatically. You have several options for database setup and management.

## Database Creation Options

### Option 1: Auto-Create During ETL (Recommended)
```bash
# Create schema automatically if it doesn't exist, then run ETL
python -m etl.run_etl --create-schema --category masters --mode initial --excel "Data_processedv4.xlsx"
```

### Option 2: Create Schema Only (No Data Load)
```bash
# Just create the database schema without loading data
python -m etl.run_etl --schema-only
```

### Option 3: Manual Database Setup (Using Python)
```bash
# Create schema using Python (uses models.py)
python -c "
from etl.schema import ensure_database_schema
from etl.db import get_engine
from etl.models_loader import load_models_module

engine = get_engine()
models = load_models_module('etl/models.py')
with engine.begin() as conn:
    ensure_database_schema(conn, engine, models_module=models)
"
```

## Command Line Options

### Schema Management Flags:
- `--create-schema`: Create database schema if it doesn't exist before running ETL
- `--schema-only`: Only create schema, don't run ETL data load
- `--force-schema`: Force recreate schema (WARNING: This will drop existing tables)

### Example Commands:

#### First-Time Setup (Empty Database):
```bash
python -m etl.run_etl --create-schema --category all --mode initial --excel "Data Model + Tables + Data_processedv2.xlsx"
```

#### Schema-Only Setup:
```bash
python -m etl.run_etl --schema-only
```

#### Regular ETL (Schema Exists):
```bash
python -m etl.run_etl --category masters --mode initial --excel "Data Model + Tables + Data_processedv2.xlsx"
```

#### Daily Incremental Load:
```bash
python -m etl.run_etl --category all --mode incremental --excel "daily_data.xlsx"
```

## Database Schema Details

The database schema is created from `etl/models.py` (SQLAlchemy models):
- **78+ Tables** with all current table definitions
- **Primary keys** and **foreign key constraints** (from model definitions)
- **Indexes** for performance (defined in models)
- **Data types** from SQLAlchemy model definitions

### Table Categories:
1. **Master Tables**: Currency, Location, Material types, etc.
2. **Core Business**: Materials, Suppliers, Plants
3. **Relationship Tables**: Mappings and associations
4. **Transactional Data**: Purchase history, pricing data

## Environment Setup

Ensure your you set your env variables in your terminal contains:
```bash
# Database Connection
DB_HOST=database-1.cqv8cisuuyq1.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_password
DB_NAME=postgres

# SSH Tunnel (for private databases)
BASTION_HOST=174.129.168.239
BASTION_USER=ubuntu
BASTION_KEY_PATH=~/Desktop/bastion-ec2.pem
```

## Troubleshooting

### Schema Creation Issues:
- **Permission errors**: Ensure database user has CREATE TABLE privileges
- **Connection issues**: Verify SSH tunnel and database credentials
- **Partial creation**: Some statements may fail due to dependencies - this is normal

### ETL After Schema Creation:
- The ETL will automatically detect existing schema
- Use `--create-schema` flag for safety (checks if schema exists first)
- Schema creation is idempotent - safe to run multiple times

## Server Deployment

For your manager's testing scenario:

1. **Server Setup**:
   ```bash
   # Upload ETL files to server
   # Set up environment variables
   # Install Python dependencies
   ```

2. **One-Command Database Setup**:
   ```bash
   python -m etl.run_etl --create-schema --category all --mode initial --excel "uploaded_file.xlsx"
   ```

3. **Result**: Complete database with all tables and data loaded

## Verification

After schema creation, verify with:
```bash
# Check table count and structure
python -c "
from etl.schema import get_schema_info
from etl.tunnel import open_ssh_tunnel
from etl.db import create_engine_for_port

with open_ssh_tunnel() as port:
    engine = create_engine_for_port(port)
    with engine.connect() as conn:
        info = get_schema_info(conn)
        print(f'Tables created: {info[\"table_count\"]}')
        for table, data in info['tables'].items():
            print(f'  {table}: {data[\"rows\"]} rows')
"
```

This setup provides a complete end-to-end solution that can create the database and load data in a single command.
