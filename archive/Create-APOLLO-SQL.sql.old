-- APOLLO Database Creation Script
-- Based on database_metadata.csv analysis
-- Tables created in dependency order to avoid foreign key constraint issues

-- =====================================================
-- MASTER TABLES (No dependencies)
-- =====================================================

-- 1. Currency Master
CREATE TABLE "currency_master" (
	"currency_id" INTEGER PRIMARY KEY,
	"currency_name" VARCHAR(10) NOT NULL,
	"currency_desc" VARCHAR(50) NOT NULL
);

-- 2. Location Type Master
CREATE TABLE "location_type_master" (
	"location_type_id" INTEGER PRIMARY KEY,
	"location_type_desc" VARCHAR(50) NOT NULL
);

-- 3. Location Master
CREATE TABLE "location_master" (
	"location_id" INTEGER PRIMARY KEY,
	"location_name" VARCHAR(100) NOT NULL,
	"location_type_id" INTEGER NOT NULL,
	"parent_location_id" INTEGER,
	FOREIGN KEY ("location_type_id") REFERENCES "location_type_master"("location_type_id"),
	FOREIGN KEY ("parent_location_id") REFERENCES "location_master"("location_id")
);

-- 4. Calendar Master
CREATE TABLE "calendar_master" (
	"date" DATE PRIMARY KEY,
	"day" VARCHAR(20) NOT NULL,
	"week" INTEGER NOT NULL,
	"month" VARCHAR(20) NOT NULL,
	"quarter" VARCHAR(10) NOT NULL,
	"year" INTEGER NOT NULL,
	"customer_specific_week" VARCHAR(50),
	"customer_specific_quarter" VARCHAR(50)
);

-- 5. Frequency Master
CREATE TABLE "frequency_master" (
	"frequency_of_update_id" INTEGER PRIMARY KEY,
	"frequency_of_update_desc" VARCHAR(50) NOT NULL
);

-- 6. Repeat Master
CREATE TABLE "repeat_master" (
	"repeat_master_id" INTEGER PRIMARY KEY,
	"frequency_of_update_id" INTEGER NOT NULL,
	"frequency_of_update_desc" VARCHAR(50) NOT NULL,
	"repeat_choices" VARCHAR(100) NOT NULL,
	FOREIGN KEY ("frequency_of_update_id") REFERENCES "frequency_master"("frequency_of_update_id")
);

-- 7. Pricing Source Master
CREATE TABLE "pricing_source_master" (
	"source_of_price_id" INTEGER PRIMARY KEY,
	"source_of_price_name" VARCHAR(100) NOT NULL,
	"credentials_api_key" VARCHAR(255),
	"user_id" VARCHAR(100),
	"pwd" VARCHAR(255)
);

-- 8. Material Type Master
CREATE TABLE "material_type_master" (
	"material_type_master_id" INTEGER PRIMARY KEY,
	"material_type_master_desc" VARCHAR(50) NOT NULL
);

-- 9. News Tags
CREATE TABLE "news_tags" (
	"news_tag_id" INTEGER PRIMARY KEY,
	"news_tag_description" VARCHAR(100) NOT NULL,
	"news_synonyms" VARCHAR(500) NOT NULL
);

-- 10. Pricing Type Master
CREATE TABLE "pricing_type_master" (
	"price_type_id" INTEGER PRIMARY KEY,
	"price_type_desc" VARCHAR(100) NOT NULL,
	"source_of_price" VARCHAR(100),
	"frequency_of_update" VARCHAR(50)
);

-- 11. UoM Master
CREATE TABLE "uom_master" (
	"uom_id" INTEGER PRIMARY KEY,
	"uom_name" VARCHAR(50) NOT NULL,
	"uom_symbol" VARCHAR(20) NOT NULL,
	"what_does_it_measure" VARCHAR(50) NOT NULL,
	"uom_system" VARCHAR(20) NOT NULL,
	"uom_synonyms" VARCHAR(500)
);

-- 12. UoM Conversion
CREATE TABLE "uom_conversion" (
	"id" INTEGER PRIMARY KEY,
	"from_uom_name" VARCHAR(50) NOT NULL,
	"to_uom_name" VARCHAR(50) NOT NULL,
	"what_does_it_measure" VARCHAR(50) NOT NULL,
	"conversion_factor" DECIMAL(15,6) NOT NULL, --// needs change 
	"syn" VARCHAR(500)
);

ALTER TABLE "uom_conversion"
ALTER COLUMN "conversion_factor" TYPE DECIMAL(15,6);

-- 13. Purchasing Organizations
CREATE TABLE "purchasing_organizations" (
	"purchasing_org_id" INTEGER PRIMARY KEY,
	"purchasing_org_desc" VARCHAR(100) NOT NULL
);

-- 14. Port Master
CREATE TABLE "port_master" (
	"port_id" INTEGER PRIMARY KEY,
	"port" VARCHAR(100) NOT NULL
);

/* 1. Create an enum for freight modes */
CREATE TYPE freight_mode_enum AS ENUM ('SEA', 'AIR', 'RAIL', 'MULTI');

/* 2. Add the column to the existing table */
ALTER TABLE port_master
    ADD COLUMN freight_mode freight_mode_enum NOT NULL DEFAULT 'SEA';

/* 3. Populate the table */
INSERT INTO port_master (port_id, port, freight_mode) VALUES
/* ---------- INDIA – Ports served by Ocean vessels ---------- */
( 1, 'JNPT - Jawaharlal Nehru Port, Navi Mumbai',           'SEA'),
( 2, 'Mumbai Port Trust – Mumbai',                          'SEA'),
( 3, 'Mundra Port – Gujarat',                               'SEA'),
( 4, 'Pipavav Port – Gujarat',                              'SEA'),
( 5, 'Kandla Port – Deendayal Port Trust, Gujarat',         'SEA'),
( 6, 'Dahej Port – Gujarat',                                'SEA'),
( 7, 'Hazira Port – Gujarat',                               'SEA'),
( 8, 'Tuticorin Port – V.O. Chidambaranar Port, Tamil Nadu','SEA'),
( 9, 'Chennai Port – Tamil Nadu',                           'SEA'),
(10, 'Ennore Port – Kamarajar Port, Tamil Nadu',            'SEA'),
(11, 'Visakhapatnam Port – Andhra Pradesh',                 'SEA'),
(12, 'Haldia Port – West Bengal',                           'SEA'),
(13, 'Kolkata Dock System – West Bengal',                   'SEA'),
(14, 'Paradip Port – Odisha',                               'SEA'),

/* ---------- INDIA – Inland Container Depots (Rail) ---------- */
(15, 'ICD Silvassa – Dadra & Nagar Haveli',                 'RAIL'),
(16, 'ICD Dadri – Uttar Pradesh',                           'RAIL'),
(17, 'ICD Tughlakabad – New Delhi',                         'RAIL'),
(18, 'ICD Pune – Maharashtra',                              'RAIL'),
(19, 'ICD Ahmedabad – Gujarat',                             'RAIL'),
(20, 'ICD Hyderabad – Telangana',                           'RAIL'),

/* ---------- BRAZIL – Ocean ports ---------- */
(21, 'Port of Santos – São Paulo',                          'SEA'),
(22, 'Port of Rio de Janeiro – Rio de Janeiro',             'SEA'),
(23, 'Port of Itaguaí – Sepetiba Bay, Rio de Janeiro',      'SEA'),
(24, 'Port of Paranaguá – Paraná',                          'SEA'),
(25, 'Port of Suape – Pernambuco',                          'SEA'),
(26, 'Port of Itajaí – Santa Catarina',                     'SEA'),
(27, 'Port of Vitória – Espírito Santo',                    'SEA'),
(28, 'Port of Salvador – Bahia',                            'SEA'),
(29, 'Port of Pecém – Ceará',                               'SEA'),
(30, 'Port of Rio Grande – Rio Grande do Sul',              'SEA');

-- 15. Forex Conversion Options Master
CREATE TABLE "forex_conversion_options_master" (
	"forex_conversion_id" INTEGER PRIMARY KEY,
	"forex_conversion_method" VARCHAR(200) NOT NULL
);

-- =====================================================
-- CORE BUSINESS TABLES
-- =====================================================

-- 16. Material Master
CREATE TABLE "material_master" (
	"material_id" VARCHAR(20) PRIMARY KEY,
	"material_description" VARCHAR(200) NOT NULL,
	"material_type" VARCHAR(50) NOT NULL,
	"material_status" VARCHAR(20) NOT NULL,
	"material_category" VARCHAR(50) NOT NULL,
	"base_uom_id" INTEGER NOT NULL,
	"base_uom_desc" VARCHAR(50) NOT NULL,
	"cas_no" VARCHAR(50),
	"unspsc_code" VARCHAR(50),
	"hsn_code" VARCHAR(50),
	"user_defined_material_desc" VARCHAR(200),
	FOREIGN KEY ("base_uom_id") REFERENCES "uom_master"("uom_id"),
	FOREIGN KEY ("material_type") REFERENCES "material_type_master"("material_type_master_desc")
);

-- 17. Supplier Master
CREATE TABLE "supplier_master" (
	"supplier_id" INTEGER PRIMARY KEY,
	"supplier_name" VARCHAR(200) NOT NULL,
	"supplier_plant_name" VARCHAR(200) NOT NULL,
	"supplier_status" VARCHAR(20) NOT NULL,
	"supplier_country_id" INTEGER,
	"supplier_country_name" VARCHAR(100),
	"base_currency_id" INTEGER,
	"relevant_country_region" VARCHAR(100),
	"user_defined_supplier_desc" VARCHAR(200),
	"supplier_duns" VARCHAR(50),
	FOREIGN KEY ("supplier_country_id") REFERENCES "location_master"("location_id"),
	FOREIGN KEY ("base_currency_id") REFERENCES "currency_master"("currency_id")
);


-- 18. User Master
CREATE TABLE "user_master" (
	"user_id" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
	"user_email" VARCHAR(255)
);

-- 19. Country Master
CREATE TABLE "country_master" (
	"country_id" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
	"country_code" VARCHAR(10),
	"country_name" VARCHAR(100)
);

-- 20. Purchaser Plant Master
CREATE TABLE "purchaser_plant_master" (
	"plant_id" INTEGER PRIMARY KEY,
	"plant_name" VARCHAR(100) NOT NULL,
	"plant_country_code" VARCHAR(100),
	"base_currency_accounting" VARCHAR(10),
	"special_economic_zone" VARCHAR(5),
	FOREIGN KEY ("plant_country_code") REFERENCES "country_master"("country_code"),
	FOREIGN KEY ("base_currency_accounting") REFERENCES "currency_master"("currency_name")
);

-- 21. Incoterms Master
CREATE TABLE "incoterms_master" (
	"incoterm_id" INTEGER PRIMARY KEY,
	"inco_term_name" VARCHAR(10) NOT NULL,
	"inco_term_desc" VARCHAR(200) NOT NULL,
	"transport_modes_where_used" VARCHAR(100) NOT NULL,
	"packaging_charges" VARCHAR(50) NOT NULL,
	"loading_charges" VARCHAR(50) NOT NULL,
	"delivery_to_port" VARCHAR(50) NOT NULL,
	"export_duty_taxes" VARCHAR(50) NOT NULL,
	"origin_terminal_charges" VARCHAR(50) NOT NULL,
	"loading_on_carriage" VARCHAR(50) NOT NULL,
	"carriage_freight_charges" VARCHAR(50) NOT NULL,
	"insurance" VARCHAR(50) NOT NULL,
	"destination_terminal_charges" VARCHAR(50) NOT NULL,
	"delivery_to_destination_charge" VARCHAR(50) NOT NULL,
	"import_duty_taxes" VARCHAR(50) NOT NULL
);



-- =====================================================
-- RELATIONSHIP TABLES
-- =====================================================

-- 22. Plant Material Purchase Org Supplier
CREATE TABLE "plant_material_purchase_org_supplier" (
	"porg_plant_material_id" VARCHAR(50) PRIMARY KEY,
	"plant_id" INTEGER NOT NULL,
	"plant_name" VARCHAR(100) NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"material_name" VARCHAR(200),
	"purchasing_org_id" INTEGER NOT NULL,
	"user_id" INTEGER,
	"supplier_id" INTEGER NOT NULL,
	"supplier_name" VARCHAR(200) NOT NULL,
	"supplier_plant" VARCHAR(200) NOT NULL,
	"valid_from" DATE,
	"valid_to" DATE,
	"user_purchase_org_id" INTEGER,
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id")
);

-- 23. User Purchase Org
CREATE TABLE "user_purchase_org" (
	"user_purchase_org_id" INTEGER PRIMARY KEY,
	"purchase_org_id" INTEGER,
	"user_id" INTEGER,
	FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id")
);

-- 24. Where To Use Each Price Type
CREATE TABLE "where_to_use_each_price_type" (
	"porg_material_price_type_id" VARCHAR(50) PRIMARY KEY,
	"material_id" VARCHAR(20) NOT NULL,
	"material_description" VARCHAR(200) NOT NULL,
	"purchasing_org_id" INTEGER,
	"price_type_id" INTEGER NOT NULL,
	"price_type_desc" VARCHAR(100) NOT NULL,
	"source_of_price_id" INTEGER NOT NULL,
	"data_series_to_extract_from_source" VARCHAR(200) NOT NULL,
	"data_series_pricing_market" VARCHAR(100),
	"data_series_incoterm" VARCHAR(50),
	"data_series_currency" VARCHAR(10),
	"data_series_uom" VARCHAR(20),
	"frequency_of_update_id" INTEGER NOT NULL,
	"repeat_choice" VARCHAR(100) NOT NULL,
	"use_in_cost_sheet" VARCHAR(5),
	"use_in_price_benchmarking" VARCHAR(5),
	"use_in_spend_analytics" VARCHAR(5),
	"last_updated_on" TIMESTAMP,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("price_type_id") REFERENCES "pricing_type_master"("price_type_id"),
	FOREIGN KEY ("source_of_price_id") REFERENCES "pricing_source_master"("source_of_price_id"),
	FOREIGN KEY ("frequency_of_update_id") REFERENCES "frequency_master"("frequency_of_update_id")
);

-- 25. Tile Cost Sheet Chemical Reaction
CREATE TABLE "tile_cost_sheet_chemical_reaction_master_data" (
	"m_cr_rrm_id" VARCHAR(50) PRIMARY KEY,
	"material_id" VARCHAR(20) NOT NULL,
	"material_desc" VARCHAR(200) NOT NULL,
	"chemical_reaction_id" INTEGER NOT NULL,
	"reaction_raw_material_id" VARCHAR(20) NOT NULL,
	"reaction_raw_material_desc" VARCHAR(200) NOT NULL,
	"reaction_raw_material_cas_no" VARCHAR(50),
	"material_base_uom_id" INTEGER NOT NULL,
	"material_base_uom_name" VARCHAR(50) NOT NULL,
	"reaction_raw_material_base_uom_id" INTEGER NOT NULL,
	"reaction_raw_material_base_uom_name" VARCHAR(50) NOT NULL,
	"reaction_raw_material_1_consumption" DECIMAL(10,3) NOT NULL,
	"valid_from" DATE NOT NULL,
	"valid_to" DATE NOT NULL,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("material_base_uom_id") REFERENCES "uom_master"("uom_id"),
	FOREIGN KEY ("reaction_raw_material_base_uom_id") REFERENCES "uom_master"("uom_id")
);

-- 26. Currency Exchange History
CREATE TABLE "currency_exchange_history" (
	"currency_exchange_id" INTEGER PRIMARY KEY,
	"from_currency" VARCHAR(10) NOT NULL,
	"to_currency" VARCHAR(10) NOT NULL,
	"date_from" DATE NOT NULL,
	"date_to" DATE NOT NULL,
	"multiplier" DECIMAL(10,6) NOT NULL,
	"purchase_org_id" VARCHAR(20) NOT NULL,
	FOREIGN KEY ("from_currency") REFERENCES "currency_master"("currency_name"),
	FOREIGN KEY ("to_currency") REFERENCES "currency_master"("currency_name")
);

-- 27. Company Currency Exchange History
CREATE TABLE "company_currency_exchange_history" (
    "currency_exchange_purchase_org_id" INTEGER PRIMARY KEY,
    "from_currency" VARCHAR(10) NOT NULL,
    "to_currency" VARCHAR(10) NOT NULL,
    "date_from" DATE NOT NULL,
    "date_to" DATE NOT NULL,
    "multiplier" DECIMAL(10,6) NOT NULL,
    "purchase_org_id" INTEGER,  -- Changed from VARCHAR(20) to INTEGER
    FOREIGN KEY ("purchase_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
    FOREIGN KEY ("from_currency") REFERENCES "currency_master"("currency_name"),
    FOREIGN KEY ("to_currency") REFERENCES "currency_master"("currency_name")
);

-- 28. Ocean Freight Master
CREATE TABLE "ocean_freight_master" (
    "ocean_freight_id" INTEGER PRIMARY KEY,
    "source_port_id" INTEGER NOT NULL,      -- Changed from VARCHAR(20) to INTEGER
    "destination_port_id" INTEGER NOT NULL,
    "freight_cost" DECIMAL(10,2) NOT NULL,
    "freight_cost_currency" VARCHAR(10) NOT NULL,
    FOREIGN KEY ("destination_port_id") REFERENCES "port_master"("port_id"),
    FOREIGN KEY ("source_port_id") REFERENCES "port_master"("port_id"),
    FOREIGN KEY ("freight_cost_currency") REFERENCES "currency_master"("currency_name")
);


-- 29. Plant To Port Mapping Master
CREATE TABLE "plant_to_port_mapping_master" (
	"plant_port_id" VARCHAR(50) PRIMARY KEY,
	"plant_id" INTEGER NOT NULL,
	"plant_name" VARCHAR(100) NOT NULL,
	"port_id" INTEGER NOT NULL,
	"port_name" VARCHAR(100) NOT NULL,
	"port_country_code" VARCHAR(10) NOT NULL,
	"preferred_port" BOOLEAN NOT NULL,
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("port_id") REFERENCES "port_master"("port_id"),
	FOREIGN KEY ("port_country_code") REFERENCES "country_master"("country_code")
);

-- 30. Material Supplier General Intelligence
CREATE TABLE "material_supplier_general_intelligence" (
	"material_supplier_general_intelligence_id" VARCHAR(50) PRIMARY KEY,
	"supplier_id" INTEGER NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"supplier_name" VARCHAR(200) NOT NULL,
	"supplier_contact_name" VARCHAR(100) NOT NULL,
	"supplier_contact_email" VARCHAR(100) NOT NULL,
	"supplier_contact_mobile" VARCHAR(20) NOT NULL,
	"supplier_country_code" VARCHAR(100) NOT NULL,
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("supplier_country_code") REFERENCES "country_master"("country_code")
);

-- 31. Supplier Hierarchy
CREATE TABLE "supplier_hierarchy" (
	"supplier_hierarchy_id" INTEGER PRIMARY KEY,
	"supplier_id" INTEGER NOT NULL,
	"parent_supplier_id" INTEGER NOT NULL,
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("parent_supplier_id") REFERENCES "supplier_master"("supplier_id")
);

-- 32. Material Synonyms
CREATE TABLE "material_synonyms" (
	"synonym_id" INTEGER PRIMARY KEY,
	"material_id" VARCHAR(20) NOT NULL,
	"material_synonym" VARCHAR(200) NOT NULL,
	"synonym_language" VARCHAR(50) NOT NULL,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id")
);

-- 33. Chemical Raw Material Synonyms
CREATE TABLE "chemical_raw_material_synonyms" (
	"material_synonym_id" VARCHAR(20) PRIMARY KEY,
	"material_id_or_reaction_raw_mat" VARCHAR(20) NOT NULL,
	"synonym_name" VARCHAR(200) NOT NULL
);

-- 34. Region Hierarchy
CREATE TABLE "region_hierarchy" (
	"synonym_id" INTEGER PRIMARY KEY,
	"location_id" INTEGER NOT NULL,
	"region_name" VARCHAR(100) NOT NULL,
	"region_synonym" VARCHAR(100) NOT NULL,
	"type" VARCHAR(50) NOT NULL,
	"parent_id" INTEGER NOT NULL,
	FOREIGN KEY ("location_id") REFERENCES "location_master"("location_id")
);

-- 35. User Currency Preference
CREATE TABLE "user_currency_preference" (
	"user_id" INTEGER PRIMARY KEY,
	"user_preferred_currency" VARCHAR(10) NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id"),
	FOREIGN KEY ("user_preferred_currency") REFERENCES "currency_master"("currency_name")
);

-- 36. Settings User Material Category
CREATE TABLE "settings_user_material_category" (
	"user_material_category_id" VARCHAR(50) PRIMARY KEY,
	"user_id" INTEGER,
	"tile_market_research_summary_length" VARCHAR(50),
	"material_category" VARCHAR(50),
	"tile_news_preferred_sources" VARCHAR(100),
	"tile_cost_sheet_price_history_window" VARCHAR(100) NOT NULL,
	"tile_cost_sheet_periods" VARCHAR(100) NOT NULL,
	"tile_cost_sheet_cost_calculation" VARCHAR(100) NOT NULL,
	"tile_cost_sheet_forex_values" VARCHAR(100),
	FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id")
);

-- 37. Country HSN Code Wise Duty Structure
CREATE TABLE "country_hsn_code_wise_duty_structure" (
	"id" INTEGER PRIMARY KEY,
	"hsn_code" VARCHAR(20) NOT NULL,
	"destination_country_code" VARCHAR(100) NOT NULL,
	"net_duty" DECIMAL(10,6) NOT NULL,
	"country_of_origin_all_code" VARCHAR(100) NOT NULL,
	FOREIGN KEY ("destination_country_code") REFERENCES "country_master"("country_code"),
	FOREIGN KEY ("country_of_origin_all_code") REFERENCES "country_master"("country_code")
);

-- =====================================================
-- TRANSACTIONAL TABLES
-- =====================================================

-- 38. News Porg Plant Material Best Sources
CREATE TABLE "news_porg_plant_material_best_sources" (
	"news_porg_plant_material_id" VARCHAR(50) PRIMARY KEY,
	"plant_id" INTEGER NOT NULL,
	"material_category" INTEGER NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"purchasing_org_id" VARCHAR(20) NOT NULL,
	"supplier_id" INTEGER NOT NULL,
	"source_name" VARCHAR(100) NOT NULL,
	"login_credentials_api_key" VARCHAR(255),
	"login_credentials_user_id" VARCHAR(100),
	"login_cred_pwd_attribute_10" VARCHAR(255),
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id")
);

-- 39. News Porg Plant Material Source Data
CREATE TABLE "news_porg_plant_material_source_data" (
	"news_porg_plant_material_source_data_id" VARCHAR(50) PRIMARY KEY,
	"plant_id" INTEGER NOT NULL,
	"material_category" INTEGER NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"purchasing_org_id" VARCHAR(20) NOT NULL,
	"supplier_id" INTEGER NOT NULL,
	"source_name" VARCHAR(100) NOT NULL,
	"actual_news" TEXT NOT NULL,
	"ai_created_impact_demand_supply" VARCHAR(50) NOT NULL,
	"ai_created_impact_summarized" VARCHAR(200) NOT NULL,
	"user_id" INTEGER NOT NULL,
	"user_updates_summary" VARCHAR(200) NOT NULL,
	"reliability_of_news" VARCHAR(100) NOT NULL,
	"news_tags" JSON NOT NULL,
	"date_of_publication" TIMESTAMP NOT NULL,
	"key_takeaway" VARCHAR(500) NOT NULL,
	"user_update_date" TIMESTAMP NOT NULL,
	"active" BOOLEAN NOT NULL,
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id")
);

-- 40. Tile Cost Sheet Historical Current Supplier
CREATE TABLE "tile_cost_sheet_historical_current_supplier" (
	"porg_plant_material_supplier_date" VARCHAR(50) PRIMARY KEY,
	"plant_id" INTEGER NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"purchasing_org_id" VARCHAR(20) NOT NULL,
	"supplier_id" INTEGER NOT NULL,
	"date_of_quote" DATE NOT NULL,
	"incoterms" VARCHAR(10) NOT NULL,
	"uom_of_quote" VARCHAR(20) NOT NULL,
	"cost_at_factory_gate" DECIMAL(10,2) NOT NULL,
	"currency_cost_factory_gate" VARCHAR(10) NOT NULL,
	"cost_given_in_quote" DECIMAL(10,2) NOT NULL,
	"currency_cost_given_quote" VARCHAR(10) NOT NULL,
	"credit_terms_days" INTEGER NOT NULL,
	"country_of_origin" VARCHAR(100) NOT NULL,
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("incoterms") REFERENCES "incoterms_master"("inco_term_name"),
	FOREIGN KEY ("uom_of_quote") REFERENCES "uom_master"("uom_name"),
	FOREIGN KEY ("currency_cost_factory_gate") REFERENCES "currency_master"("currency_name"),
	FOREIGN KEY ("currency_cost_given_quote") REFERENCES "currency_master"("currency_name"),
	FOREIGN KEY ("country_of_origin") REFERENCES "country_master"("country_name")
);

-- 41. Purchase History Transactional Data
CREATE TABLE "purchase_history_transactional_data" (
	"purchase_transaction_id" VARCHAR(50) PRIMARY KEY,
	"purchasing_org_id" INTEGER NOT NULL,
	"material_id" VARCHAR(20) NOT NULL,
	"plant_id" INTEGER NOT NULL,
	"supplier_id" INTEGER NOT NULL,
	"po_number" INTEGER NOT NULL,
	"purchase_date" DATE NOT NULL,
	"currency_of_po" VARCHAR(10) NOT NULL,
	"uom" VARCHAR(20) NOT NULL,
	"quantity" DECIMAL(10,2) NOT NULL,
	"cost_per_uom" DECIMAL(10,2) NOT NULL,
	"total_cost" DECIMAL(10,2) NOT NULL,
	"payment_terms" VARCHAR(100) NOT NULL,
	"freight_terms" VARCHAR(100) NOT NULL,
	"transaction_posting_date" DATE,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
	FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id"),
	FOREIGN KEY ("currency_of_po") REFERENCES "currency_master"("currency_name"),
	FOREIGN KEY ("uom") REFERENCES "uom_master"("uom_name")
);

-- 42. Tile Multiple Point Engagements
CREATE TABLE "tile_multiple_point_engagements" (
    "porg_plant_material_supplier_date" VARCHAR(50) PRIMARY KEY,
    "plant_id" INTEGER NOT NULL,
    "material_id" VARCHAR(20) NOT NULL,
    "purchasing_org_id" INTEGER NOT NULL,
    "supplier_id" INTEGER NOT NULL,
    "date_of_meeting" DATE NOT NULL,
    "reference_email_document_id" VARCHAR(50) NOT NULL,
    "media_link" VARCHAR(500) NOT NULL,
    FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
    FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
    FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
    FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id")
);

-- 43. Tile Vendor Minutes Of Meeting
CREATE TABLE "tile_vendor_minutes_of_meeting" (
    "porg_plant_material_supplier_date" VARCHAR(50) PRIMARY KEY,
    "plant_id" INTEGER NOT NULL,
    "material_id" VARCHAR(20) NOT NULL,
    "purchasing_org_id" INTEGER NOT NULL,
    "supplier_id" INTEGER NOT NULL,
    "date_of_meeting" DATE NOT NULL,
    "reference_email_document_id" VARCHAR(50) NOT NULL,
    "media_link" VARCHAR(500) NOT NULL,
    FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
    FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
    FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id"),
    FOREIGN KEY ("supplier_id") REFERENCES "supplier_master"("supplier_id")
);

-- 44. Audit Snapshot Price Prediction Negotiation
CREATE TABLE "audit_snapshot_price_prediction_negotiation" (
    "porg_plant_material_date_id" VARCHAR(50) PRIMARY KEY,
    "purchasing_org_id" INTEGER NOT NULL,
    "material_id" VARCHAR(20) NOT NULL,
    "plant_id" INTEGER NOT NULL,
    "capacity_utilization" VARCHAR(20) NOT NULL,
    "conversion_spread" DECIMAL(10,2) NOT NULL,
    "factors_influencing_demand" TEXT NOT NULL,
    "demand_outlook" VARCHAR(20) NOT NULL,
    "factors_influencing_supply" TEXT NOT NULL,
    "supply_disruption" VARCHAR(20) NOT NULL,
    "business_cycle" VARCHAR(20) NOT NULL,
    "news_highlights" TEXT NOT NULL,
    "forecasted_value_short" DECIMAL(10,2) NOT NULL,
    "forecasted_date" DATE NOT NULL,
    "forecasted_value_long" DECIMAL(10,2) NOT NULL,
    "factors_influencing_forecast" TEXT NOT NULL,
    "forecasted_average_value" DECIMAL(10,2) NOT NULL,
    "news_insights_obj" TEXT NOT NULL,
    FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
    FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
    FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id")
);

-- 45. Settings Field Names In Table
CREATE TABLE "settings_field_names_in_table" (
	"field_name_change_id" VARCHAR(50) PRIMARY KEY,
	"table_name" VARCHAR(100) NOT NULL,
	"existing_field_name" VARCHAR(100) NOT NULL,
	"new_field_name" VARCHAR(100) NOT NULL
);

-- 46. Settings User Material Category Tile Preferences
CREATE TABLE "settings_user_material_category_tile_preferences" (
    "user_material_category_id" VARCHAR(50) PRIMARY KEY,
    "user_id" INTEGER NOT NULL,
    "tile_market_research_summary_length" VARCHAR(200) NOT NULL,
    "material_category" VARCHAR(50) NOT NULL,
    "tile_news_preferred_sources" VARCHAR(100),
    "tile_cost_sheet_price_history_window" INTEGER NOT NULL,
    "tile_cost_sheet_periods" VARCHAR(20) NOT NULL,
    "tile_cost_sheet_cost_calculation" VARCHAR(20) NOT NULL,
    "tile_cost_sheet_forex_values" VARCHAR(20),
    FOREIGN KEY ("user_id") REFERENCES "user_master"("user_id")
);

-- 47. Price Data Country Storage
CREATE TABLE "price_data_country_storage" (
	"material_plant_id" VARCHAR(50) PRIMARY KEY,
	"material_id" VARCHAR(20) NOT NULL,
	"plant_id" INTEGER NOT NULL,
	"country" VARCHAR(100) NOT NULL,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("plant_id") REFERENCES "purchaser_plant_master"("plant_id"),
	FOREIGN KEY ("country") REFERENCES "country_master"("country_name")
);

-- 48. Price History Data
CREATE TABLE "price_history_data" (
	"material_price_type_period_id" VARCHAR(50) PRIMARY KEY,
	"material_id" VARCHAR(20) NOT NULL,
	"period_start_date" DATE NOT NULL,
	"period_end_date" DATE NOT NULL,
	"country" VARCHAR(100) NOT NULL,
	"price" DECIMAL(10,2) NOT NULL,
	"price_currency" VARCHAR(10) NOT NULL,
	"price_history_source" VARCHAR(100) NOT NULL,
	"price_type" VARCHAR(50) NOT NULL,
	FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
	FOREIGN KEY ("price_currency") REFERENCES "currency_master"("currency_name")
);

-- 49. Material Research Reports
CREATE TABLE "material_research_reports" (
    "id"                serial PRIMARY KEY,
    "date"              date,
    "publication"       varchar(255),
    "report_link"       text,
    "published_date"    date,
    "material_id"       varchar(20),
    "upload_user_id"           INTEGER,
	"update_user_id"           INTEGER,
    "takeaway"          text,
    FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
    FOREIGN KEY ("upload_user_id") REFERENCES "user_master"("user_id"),
	FOREIGN KEY ("update_user_id") REFERENCES "user_master"("user_id")
);

INSERT INTO material_type_master (material_type_master_id, material_type_master_desc)
VALUES
    (5, 'Consumables'),
    (6, 'MRO');


CREATE TABLE "demand_supply_trends" (
"id" serial PRIMARY KEY,
"upload_date" date,
"source" varchar(255),
"source_link" text,
"source_published_date" date,
"material_id" varchar(20),
"upload_user_id" INTEGER,
"update_user_id" INTEGER,
"demand_impact" text,
"supply_impact" text,
"location_id" INTEGER,
FOREIGN KEY ("material_id") REFERENCES "material_master"("material_id"),
FOREIGN KEY ("upload_user_id") REFERENCES "user_master"("user_id"),
FOREIGN KEY ("update_user_id") REFERENCES "user_master"("user_id"),
FOREIGN KEY ("location_id") REFERENCES "location_master"("location_id")
);

-- =====================================================
-- ADDITIONAL FOREIGN KEY CONSTRAINTS (Not run)
-- =====================================================

-- Add foreign key for plant_material_purchase_org_supplier to purchasing_organizations
ALTER TABLE "plant_material_purchase_org_supplier"
ADD CONSTRAINT "fk_plant_material_purchase_org_supplier_purchasing_org"
FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id");

-- Add foreign key for plant_material_purchase_org_supplier to user_purchase_org
ALTER TABLE "plant_material_purchase_org_supplier"
ADD CONSTRAINT "fk_plant_material_purchase_org_supplier_user_purchase_org"
FOREIGN KEY ("user_purchase_org_id") REFERENCES "user_purchase_org"("user_purchase_org_id");

-- Add foreign key for user_purchase_org to purchasing_organizations
ALTER TABLE "user_purchase_org"
ADD CONSTRAINT "fk_user_purchase_org_purchasing_org"
FOREIGN KEY ("purchase_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id");

-- Add foreign key for where_to_use_each_price_type to purchasing_organizations
ALTER TABLE "where_to_use_each_price_type"
ADD CONSTRAINT "fk_where_to_use_each_price_type_purchasing_org"
FOREIGN KEY ("purchasing_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id");

-- Add foreign key for currency_exchange_history to purchasing_organizations
ALTER TABLE "currency_exchange_history"
ADD CONSTRAINT "fk_currency_exchange_history_purchasing_org"
FOREIGN KEY ("purchase_org_id") REFERENCES "purchasing_organizations"("purchasing_org_id");

-- Add foreign key for uom_conversion to uom_master (from_uom_name)
ALTER TABLE "uom_conversion"
ADD CONSTRAINT "fk_uom_conversion_from_uom"
FOREIGN KEY ("from_uom_name") REFERENCES "uom_master"("uom_name");

-- Add foreign key for uom_conversion to uom_master (to_uom_name)
ALTER TABLE "uom_conversion"
ADD CONSTRAINT "fk_uom_conversion_to_uom"
FOREIGN KEY ("to_uom_name") REFERENCES "uom_master"("uom_name");

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Index for frequently queried columns
CREATE INDEX "idx_material_master_material_type" ON "material_master"("material_type");
CREATE INDEX "idx_material_master_material_category" ON "material_master"("material_category");
CREATE INDEX "idx_supplier_master_supplier_country" ON "supplier_master"("supplier_country_name");
CREATE INDEX "idx_purchaser_plant_master_plant_country" ON "purchaser_plant_master"("plant_country");
CREATE INDEX "idx_plant_material_purchase_org_supplier_plant_material" ON "plant_material_purchase_org_supplier"("plant_id", "material_id");
CREATE INDEX "idx_purchase_history_transactional_data_date" ON "purchase_history_transactional_data"("purchase_date");
CREATE INDEX "idx_price_history_data_period" ON "price_history_data"("period_start_date", "period_end_date");
CREATE INDEX "idx_currency_exchange_history_dates" ON "currency_exchange_history"("date_from", "date_to");

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE "purchasing_organizations" IS 'Master table for purchasing organizations within a company';
COMMENT ON TABLE "material_master" IS 'Master table for all materials with their properties and classifications';
COMMENT ON TABLE "supplier_master" IS 'Master table for all suppliers with their details and locations';
COMMENT ON TABLE "purchaser_plant_master" IS 'Master table for company plants and their locations';
COMMENT ON TABLE "plant_material_purchase_org_supplier" IS 'Core relationship table linking plants, materials, purchasing orgs, and suppliers';
COMMENT ON TABLE "purchase_history_transactional_data" IS 'Historical purchase transaction data for analysis';
COMMENT ON TABLE "price_history_data" IS 'Historical price data for materials by country and period';
COMMENT ON TABLE "currency_exchange_history" IS 'Historical currency exchange rates for different purchasing organizations';

-- End of APOLLO Database Creation Script