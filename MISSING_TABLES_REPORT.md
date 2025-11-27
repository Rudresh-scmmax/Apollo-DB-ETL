# Missing Tables in Excel File

## Summary
- **Excel has:** 25 data tables
- **Expected:** 74 tables
- **Missing:** 49 tables

## Missing Tables by Category

### Master Tables (3 missing)
1. `country_master`
2. `user_master`
3. `chemical_raw_material_synonyms`

### Relationship Tables (6 missing)
1. `user_purchase_org`
2. `company_currency_exchange_history`
3. `country_hsn_code_wise_duty_structure`
4. `country_tariffs`
5. `ocean_freight_master`
6. `plant_to_port_mapping_master`
7. `supplier_hierarchy`

### Transactional Tables (40 missing)
1. `action_plans`
2. `audit_snapshot_price_prediction_negotiation`
3. `demand_supply_summary`
4. `demand_supply_trends`
5. `esg_tracker`
6. `export_data`
7. `fact_pack`
8. `forecast_recommendations`
9. `import_data`
10. `inventory_levels`
11. `joint_development_projects`
12. `market_research_status`
13. `material_research_reports`
14. `material_supplier_general_intelligence`
15. `material_synonyms`
16. `meeting_minutes`
17. `multiple_point_engagements`
18. `negotiation_llm_logs`
19. `negotiation_recommendations`
20. `news_insights`
21. `news_porg_plant_material_source_data`
22. `plan_assignments`
23. `porters_analysis`
24. `price_data_country_storage`
25. `price_forecast_data`
26. `price_history_data`
27. `procurement_plans`
28. `purchase_history_transactional_data`
29. `quote_comparison`
30. `reach_tracker`
31. `region_hierarchy`
32. `settings_user_material_category_tile_preferences`
33. `supplier_shutdowns`
34. `supplier_tracking`
35. `tile_cost_sheet_historical_current_supplier`
36. `tile_multiple_point_engagements`
37. `tile_vendor_minutes_of_meeting`
38. `user_master`
39. `vendor_key_information`
40. `vendor_wise_action_plan`

## Existing Tables Status

✅ **All columns present** for these tables:
- Calendar_Master
- Currency_Master
- Location Master
- Location_Type_Master
- Material_Type_Master
- Repeat_Master
- UoM Master
- currency_exchange_history
- forex_conversion_options_master
- frequency_master
- incoterms_master
- material_master
- news_tags
- plant_material_purchase_org_sup
- pricing_source_master
- pricing_type_master
- purchaser_plant_master
- purchasing_organizations
- settings_user_material_category
- supplier_master
- tile_cost_sheet_chemical_reacti
- uom_conversion
- user_currency_preference
- where_to_use_each_price_type

⚠️ **Missing columns:**
- `port_master`: Missing `freight_mode` column

## Next Steps

1. **Add missing column:**
   - Add `freight_mode` column to `port_master` sheet

2. **Add missing tables:**
   - These are new tables that were added to the database schema
   - You can either:
     - Create empty sheets with just headers (columns) for now
     - Add data for these tables if you have it
     - Leave them empty if you don't need to load data for them yet

3. **Note:** The ETL will only process tables that exist in the Excel file. Missing tables won't cause errors, but they won't be loaded either.

