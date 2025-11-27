# Schema Differences Analysis: Database Models vs ETL Configuration

Based on the SQLAlchemy models imported from your database, here are the key differences that need to be updated in your ETL configuration:

## 🔴 Critical Data Type Mismatches

### 1. **purchasing_organizations**
**Current ETL Config:**
```yaml
purchasing_org_id: str
```

**Actual Database:**
```python
purchasing_org_id: Mapped[int] = mapped_column(Integer, primary_key=True)
```

**Action Required:** Change `purchasing_org_id` from `str` to `int` in `mappings.yaml`

**New Field Missing:**
- `org_code: Mapped[Optional[str]]` - Add to mappings if needed

---

### 2. **supplier_master**
**Current ETL Config:**
```yaml
supplier_id: str
```

**Actual Database:**
```python
supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True)
```

**Action Required:** Change `supplier_id` from `str` to `int` in `mappings.yaml`

**New Fields Missing:**
- `supplier_plant_name: Mapped[str]` - **REQUIRED** (NOT NULL)
- `supplier_status: Mapped[str]` - **REQUIRED** (NOT NULL)
- `supplier_country_id: Mapped[Optional[int]]` - Foreign key to `location_master.location_id`
- `supplier_country_name: Mapped[Optional[str]]`
- `base_currency_id: Mapped[Optional[int]]` - Foreign key to `currency_master.currency_id` (changed from `base_currency_accounting`)

**Fields Changed:**
- `base_currency_accounting` → Now references `currency_master.currency_id` (integer FK) instead of currency name

---

### 3. **purchaser_plant_master**
**Current ETL Config:**
```yaml
plant_id: str
plant_country: str  # ❌ Wrong field name
nearest_port: str
logistic_cost_per_container: int
```

**Actual Database:**
```python
plant_id: Mapped[int] = mapped_column(Integer, primary_key=True)
plant_country_code: Mapped[Optional[str]]  # ✅ Correct field name
special_economic_zone: Mapped[Optional[str]]  # Changed from bool to str
```

**Action Required:**
- Change `plant_id` from `str` to `int`
- Change `plant_country` → `plant_country_code` in column_renames
- Remove `nearest_port` and `logistic_cost_per_container` (not in database)
- Change `special_economic_zone` from `bool` to `str`

---

### 4. **plant_material_purchase_org_supplier**
**Current ETL Config:**
```yaml
plant_id: str
purchasing_org_id: str
supplier_id: str
```

**Actual Database:**
```python
plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
purchasing_org_id: Mapped[str] = mapped_column(String(20), nullable=False)  # Still String!
supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
```

**Action Required:**
- Change `plant_id` from `str` to `int`
- Keep `purchasing_org_id` as `str` (it's String(20) in database)
- Change `supplier_id` from `str` to `int`

**New Fields Missing:**
- `plant_name: Mapped[str]` - **REQUIRED** (NOT NULL)
- `supplier_name: Mapped[str]` - **REQUIRED** (NOT NULL)
- `supplier_plant: Mapped[str]` - **REQUIRED** (NOT NULL)
- `material_name: Mapped[Optional[str]]`

**Fields Changed:**
- `User_ID` → `user_id` (lowercase, and now Optional[int] instead of int)
- `User_Purchase_Org_ID` → `user_purchase_org_id` (lowercase)

---

### 5. **currency_exchange_history**
**Current ETL Config:**
```yaml
purchase_org_id: str
```

**Actual Database:**
```python
purchase_org_id: Mapped[str] = mapped_column(String(20), nullable=False)
```

**Status:** ✅ Correct (already String)

---

### 6. **where_to_use_each_price_type**
**Current ETL Config:**
```yaml
purchasing_org_id: str
```

**Actual Database:**
```python
purchasing_org_id: Mapped[Optional[str]] = mapped_column(String(20))
```

**Status:** ✅ Correct (already String, but now Optional)

**New Fields Missing:**
- `material_description: Mapped[str]` - **REQUIRED**
- `price_type_desc: Mapped[str]` - **REQUIRED**
- `data_series_to_extract_from_source: Mapped[str]` - **REQUIRED**
- `frequency_of_update_id: Mapped[int]` - **REQUIRED** (FK to frequency_master)
- `repeat_choice: Mapped[str]` - **REQUIRED**
- `data_series_pricing_market: Mapped[Optional[str]]`
- `data_series_incoterm: Mapped[Optional[str]]`
- `data_series_currency: Mapped[Optional[str]]`
- `data_series_uom: Mapped[Optional[str]]`
- `use_in_cost_sheet: Mapped[Optional[str]]` - Changed from bool to str
- `use_in_price_benchmarking: Mapped[Optional[str]]` - Changed from bool to str
- `use_in_spend_analytics: Mapped[Optional[str]]` - Changed from bool to str
- `last_updated_on: Mapped[Optional[datetime.datetime]]`

---

## 🟡 Foreign Key Constraint Updates

### Update `etl/load.py` - `fk_constraints` dictionary:

**Current:**
```python
fk_constraints = {
    'plant_material_purchase_org_supplier': [
        ('material_id', 'material_master', 'material_id'),
        ('supplier_id', 'supplier_master', 'supplier_id'),
        ('plant_id', 'purchaser_plant_master', 'plant_id'),
        ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
    ],
}
```

**Should be (if purchasing_org_id is still String, this might need adjustment):**
```python
fk_constraints = {
    'plant_material_purchase_org_supplier': [
        ('material_id', 'material_master', 'material_id'),
        ('supplier_id', 'supplier_master', 'supplier_id'),  # Now Integer
        ('plant_id', 'purchaser_plant_master', 'plant_id'),  # Now Integer
        # Note: purchasing_org_id FK might need special handling if it's String
    ],
    'supplier_master': [
        ('supplier_country_id', 'location_master', 'location_id'),
        ('base_currency_id', 'currency_master', 'currency_id'),
    ],
    'purchaser_plant_master': [
        ('plant_country_code', 'country_master', 'country_code'),
        ('base_currency_accounting', 'currency_master', 'currency_name'),
    ],
}
```

---

## 📋 Summary of Required Changes

### Priority 1: Data Type Fixes (Will cause ETL failures)
1. ✅ `purchasing_organizations.purchasing_org_id`: `str` → `int`
2. ✅ `supplier_master.supplier_id`: `str` → `int`
3. ✅ `purchaser_plant_master.plant_id`: `str` → `int`
4. ✅ `plant_material_purchase_org_supplier.plant_id`: `str` → `int`
5. ✅ `plant_material_purchase_org_supplier.supplier_id`: `str` → `int`

### Priority 2: Column Name Changes
1. ✅ `purchaser_plant_master.plant_country` → `plant_country_code`
2. ✅ `plant_material_purchase_org_supplier.User_ID` → `user_id`
3. ✅ `plant_material_purchase_org_supplier.User_Purchase_Org_ID` → `user_purchase_org_id`

### Priority 3: Missing Required Fields
1. ✅ `supplier_master.supplier_plant_name` (REQUIRED)
2. ✅ `supplier_master.supplier_status` (REQUIRED)
3. ✅ `plant_material_purchase_org_supplier.plant_name` (REQUIRED)
4. ✅ `plant_material_purchase_org_supplier.supplier_name` (REQUIRED)
5. ✅ `plant_material_purchase_org_supplier.supplier_plant` (REQUIRED)

### Priority 4: Field Type Changes
1. ✅ `purchaser_plant_master.special_economic_zone`: `bool` → `str`
2. ✅ `where_to_use_each_price_type.use_in_cost_sheet`: `bool` → `str`
3. ✅ `where_to_use_each_price_type.use_in_price_benchmarking`: `bool` → `str`
4. ✅ `where_to_use_each_price_type.use_in_spend_analytics`: `bool` → `str`

### Priority 5: Removed Fields
1. ✅ Remove `purchaser_plant_master.nearest_port`
2. ✅ Remove `purchaser_plant_master.logistic_cost_per_container`

---

## 🔧 Next Steps

1. Update `etl/config/mappings.yaml` with all the changes above
2. Update `etl/config/tables.yaml` if primary keys changed
3. Update `etl/load.py` FK constraints
4. Update `Create-APOLLO-SQL.sql` to match the actual database schema
5. Test with a small dataset to verify all changes work

Would you like me to create the updated configuration files with all these changes?

