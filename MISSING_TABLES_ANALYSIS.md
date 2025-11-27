# Missing Tables Analysis

Based on the SQLAlchemy models you provided, here are the tables that are NOT currently in the ETL configuration:

## Master Tables (Missing)
1. **admin_user** - Admin user authentication
2. **country_master** - Country reference data
3. **chemical_raw_material_synonyms** - Material synonyms
4. **emails** - Email storage
5. **quote_compare** - Quote comparison
6. **settings_field_names_in_table** - Field name settings
7. **tiles** - Tiles configuration
8. **user_master** - User management

## Relationship Tables (Missing)
9. **user_purchase_org** - User-purchase org relationships
10. **company_currency_exchange_history** - Company-level currency exchange
11. **country_hsn_code_wise_duty_structure** - Country duty structures
12. **country_tariffs** - Country tariff information
13. **ocean_freight_master** - Ocean freight rates
14. **plant_to_port_mapping_master** - Plant-port mappings
15. **supplier_hierarchy** - Supplier hierarchy relationships

## Transactional Tables (Missing)
16. **action_plans** - Action plans
17. **audit_snapshot_price_prediction_negotiation** - Price prediction audit
18. **demand_supply_summary** - Demand/supply summaries
19. **demand_supply_trends** - Demand/supply trends
20. **esg_tracker** - ESG tracking
21. **export_data** - Export data
22. **fact_pack** - Fact pack documents
23. **forecast_recommendations** - Forecast recommendations
24. **import_data** - Import data
25. **inventory_levels** - Inventory levels
26. **joint_development_projects** - Joint development projects
27. **material_research_reports** - Material research reports
28. **material_supplier_general_intelligence** - Supplier intelligence
29. **material_synonyms** - Material synonyms
30. **meeting_minutes** - Meeting minutes
31. **multiple_point_engagements** - Multiple point engagements
32. **negotiation_llm_logs** - Negotiation LLM logs
33. **negotiation_recommendations** - Negotiation recommendations
34. **news_insights** - News insights
35. **news_porg_plant_material_source_data** - News source data
36. **plan_assignments** - Plan assignments
37. **porters_analysis** - Porter's analysis
38. **price_data_country_storage** - Price data storage
39. **price_forecast_data** - Price forecast data
40. **price_history_data** - Price history data
41. **procurement_plans** - Procurement plans
42. **purchase_history_transactional_data** - Purchase history
43. **quote_comparison** - Quote comparison
44. **reach_tracker** - REACH tracking
45. **region_hierarchy** - Region hierarchy
46. **settings_user_material_category_tile_preferences** - User tile preferences
47. **supplier_shutdowns** - Supplier shutdowns
48. **supplier_tracking** - Supplier tracking
49. **tile_cost_sheet_historical_current_supplier** - Cost sheet historical data
50. **tile_multiple_point_engagements** - Tile MPE data
51. **tile_vendor_minutes_of_meeting** - Tile vendor MoM
52. **vendor_key_information** - Vendor key information
53. **vendor_wise_action_plan** - Vendor action plans
54. **market_research_status** - Market research status

## Total Missing: ~54 tables

These tables need to be added to:
1. `etl/config/tables.yaml` - Primary key definitions
2. `etl/config/mappings.yaml` - Table mappings and load order
3. Potentially `etl/load.py` - FK constraints if needed

