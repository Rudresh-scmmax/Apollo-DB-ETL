# New Tables Added to ETL Configuration

## Summary
I've added **54 new tables** to the ETL configuration based on your SQLAlchemy models.

## ✅ Fully Configured Tables

### Master Tables
1. **country_master** - Country reference data
2. **user_master** - User management
3. **chemical_raw_material_synonyms** - Material synonyms

### Relationship Tables
4. **user_purchase_org** - User-purchase org relationships
5. **company_currency_exchange_history** - Company-level currency exchange
6. **country_hsn_code_wise_duty_structure** - Country duty structures
7. **country_tariffs** - Country tariff information
8. **ocean_freight_master** - Ocean freight rates
9. **plant_to_port_mapping_master** - Plant-port mappings
10. **supplier_hierarchy** - Supplier hierarchy relationships

### Transactional Tables (Fully Configured)
11. **action_plans** - Action plans
12. **purchase_history_transactional_data** - Purchase history
13. **price_history_data** - Price history
14. **quote_comparison** - Quote comparison
15. **export_data** - Export data
16. **import_data** - Import data

## ⚠️ Tables Added to Load Order (Need Column Mappings)

These tables are in the `load_order` and have primary keys defined, but need column mappings configured based on your Excel structure:

### Transactional Tables
- audit_snapshot_price_prediction_negotiation
- demand_supply_summary
- demand_supply_trends
- esg_tracker
- fact_pack
- forecast_recommendations
- inventory_levels
- joint_development_projects
- material_research_reports
- material_supplier_general_intelligence
- material_synonyms
- meeting_minutes
- multiple_point_engagements
- negotiation_llm_logs
- negotiation_recommendations
- news_insights
- news_porg_plant_material_source_data
- plan_assignments
- porters_analysis
- price_data_country_storage
- price_forecast_data
- procurement_plans
- reach_tracker
- region_hierarchy
- settings_user_material_category_tile_preferences
- supplier_shutdowns
- supplier_tracking
- tile_cost_sheet_historical_current_supplier
- tile_multiple_point_engagements
- tile_vendor_minutes_of_meeting
- vendor_key_information
- vendor_wise_action_plan
- market_research_status

## Next Steps

1. **For Fully Configured Tables:**
   - Test with your Excel files
   - Adjust column_renames if Excel column names differ
   - Verify data types match your data

2. **For Tables Needing Column Mappings:**
   - Add `column_renames` section mapping Excel columns → database columns
   - Add all required columns to `dtypes` section
   - Test with sample data

3. **Optional Tables (Not in Load Order):**
   - `admin_user` - Usually managed by application
   - `emails` - Usually populated by email service
   - `quote_compare` - Check if this is different from `quote_comparison`
   - `settings_field_names_in_table` - Configuration table
   - `tiles` - Configuration table

## How to Add Column Mappings

For each table that needs mappings, add a configuration like this:

```yaml
  table_name:
    target_table: table_name
    column_renames:
      excel_column_name: database_column_name
      another_excel_col: another_db_col
    dtypes:
      database_column_name: int|str|float|date|bool|dict
      another_db_col: str
    incremental:
      strategy: business_key_upsert
```

## Files Updated

1. ✅ `etl/config/tables.yaml` - Added primary keys for all 54 tables
2. ✅ `etl/config/mappings.yaml` - Added table configurations and load order

## Notes

- All tables are set to use `business_key_upsert` strategy
- Primary keys are correctly defined based on your models
- Foreign key constraints may need to be added to `etl/load.py` for tables with FKs
- Some tables may need special transformations (add to `etl/transform.py` if needed)

