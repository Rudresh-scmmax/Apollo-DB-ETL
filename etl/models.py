from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Identity, Index, Integer, JSON, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AdminUser(Base):
    __tablename__ = 'admin_user'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='admin_user_pkey'),
        Index('ix_admin_user_id', 'id'),
        Index('ix_admin_user_username', 'username', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)


class CalendarMaster(Base):
    __tablename__ = 'calendar_master'
    __table_args__ = (
        PrimaryKeyConstraint('date', name='calendar_master_pkey'),
    )

    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[str] = mapped_column(String(20), nullable=False)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_specific_week: Mapped[Optional[str]] = mapped_column(String(50))
    customer_specific_quarter: Mapped[Optional[str]] = mapped_column(String(20))


class ChemicalRawMaterialSynonyms(Base):
    __tablename__ = 'chemical_raw_material_synonyms'
    __table_args__ = (
        PrimaryKeyConstraint('material_synonym_id', name='chemical_raw_material_synonyms_pkey'),
    )

    material_synonym_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    material_id_or_reaction_raw_mat: Mapped[str] = mapped_column(String(20), nullable=False)
    synonym_name: Mapped[str] = mapped_column(String(200), nullable=False)


class CountryMaster(Base):
    __tablename__ = 'country_master'
    __table_args__ = (
        PrimaryKeyConstraint('country_id', name='country_master_pkey'),
        UniqueConstraint('country_code', name='uk_country_code'),
        UniqueConstraint('country_name', name='uk_country_name')
    )

    country_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(10))
    country_name: Mapped[Optional[str]] = mapped_column(String(100))

    country_hsn_code_wise_duty_structure: Mapped[list['CountryHsnCodeWiseDutyStructure']] = relationship('CountryHsnCodeWiseDutyStructure', foreign_keys='[CountryHsnCodeWiseDutyStructure.country_of_origin_all_code]', back_populates='country_master')
    country_hsn_code_wise_duty_structure_: Mapped[list['CountryHsnCodeWiseDutyStructure']] = relationship('CountryHsnCodeWiseDutyStructure', foreign_keys='[CountryHsnCodeWiseDutyStructure.destination_country_code]', back_populates='country_master_')
    country_tariffs: Mapped[list['CountryTariffs']] = relationship('CountryTariffs', back_populates='country')
    purchaser_plant_master: Mapped[list['PurchaserPlantMaster']] = relationship('PurchaserPlantMaster', back_populates='country_master')
    plant_to_port_mapping_master: Mapped[list['PlantToPortMappingMaster']] = relationship('PlantToPortMappingMaster', back_populates='country_master')
    price_data_country_storage: Mapped[list['PriceDataCountryStorage']] = relationship('PriceDataCountryStorage', back_populates='country_master')
    material_supplier_general_intelligence: Mapped[list['MaterialSupplierGeneralIntelligence']] = relationship('MaterialSupplierGeneralIntelligence', back_populates='country_master')
    quote_comparison: Mapped[list['QuoteComparison']] = relationship('QuoteComparison', back_populates='country')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='country_master')


class CurrencyMaster(Base):
    __tablename__ = 'currency_master'
    __table_args__ = (
        PrimaryKeyConstraint('currency_id', name='currency_master_pkey'),
        UniqueConstraint('currency_name', name='uk_currency_name')
    )

    currency_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency_name: Mapped[str] = mapped_column(String(5), nullable=False)
    currency_desc: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[list['UserMaster']] = relationship('UserMaster', secondary='user_preference_currency', back_populates='currency')
    user_: Mapped[list['UserMaster']] = relationship('UserMaster', secondary='user_currency_preference', back_populates='currency_master')
    company_currency_exchange_history: Mapped[list['CompanyCurrencyExchangeHistory']] = relationship('CompanyCurrencyExchangeHistory', foreign_keys='[CompanyCurrencyExchangeHistory.from_currency]', back_populates='currency_master')
    company_currency_exchange_history_: Mapped[list['CompanyCurrencyExchangeHistory']] = relationship('CompanyCurrencyExchangeHistory', foreign_keys='[CompanyCurrencyExchangeHistory.to_currency]', back_populates='currency_master_')
    currency_exchange_history: Mapped[list['CurrencyExchangeHistory']] = relationship('CurrencyExchangeHistory', foreign_keys='[CurrencyExchangeHistory.from_currency]', back_populates='currency_master')
    currency_exchange_history_: Mapped[list['CurrencyExchangeHistory']] = relationship('CurrencyExchangeHistory', foreign_keys='[CurrencyExchangeHistory.to_currency]', back_populates='currency_master_')
    ocean_freight_master: Mapped[list['OceanFreightMaster']] = relationship('OceanFreightMaster', back_populates='currency_master')
    purchaser_plant_master: Mapped[list['PurchaserPlantMaster']] = relationship('PurchaserPlantMaster', back_populates='currency_master')
    price_history_data: Mapped[list['PriceHistoryData']] = relationship('PriceHistoryData', back_populates='currency_master')
    supplier_master: Mapped[list['SupplierMaster']] = relationship('SupplierMaster', back_populates='base_currency')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='currency_master')
    quote_comparison: Mapped[list['QuoteComparison']] = relationship('QuoteComparison', back_populates='currency')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', foreign_keys='[TileCostSheetHistoricalCurrentSupplier.currency_cost_factory_gate]', back_populates='currency_master')
    tile_cost_sheet_historical_current_supplier_: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', foreign_keys='[TileCostSheetHistoricalCurrentSupplier.currency_cost_given_quote]', back_populates='currency_master_')


class Emails(Base):
    __tablename__ = 'emails'
    __table_args__ = (
        PrimaryKeyConstraint('gmail_id', name='emails_pkey'),
        Index('idx_emails_received_at', 'received_at')
    )

    gmail_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    joint_development_projects: Mapped['JointDevelopmentProjects'] = relationship('JointDevelopmentProjects', uselist=False, back_populates='gmail')
    meeting_minutes: Mapped['MeetingMinutes'] = relationship('MeetingMinutes', uselist=False, back_populates='gmail')
    multiple_point_engagements: Mapped['MultiplePointEngagements'] = relationship('MultiplePointEngagements', uselist=False, back_populates='gmail')
    vendor_wise_action_plan: Mapped[list['VendorWiseActionPlan']] = relationship('VendorWiseActionPlan', back_populates='gmail')


class ForexConversionOptionsMaster(Base):
    __tablename__ = 'forex_conversion_options_master'
    __table_args__ = (
        PrimaryKeyConstraint('forex_conversion_id', name='forex_conversion_options_master_pkey'),
    )

    forex_conversion_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    forex_conversion_method: Mapped[str] = mapped_column(String(200), nullable=False)


class FrequencyMaster(Base):
    __tablename__ = 'frequency_master'
    __table_args__ = (
        PrimaryKeyConstraint('frequency_of_update_id', name='frequency_master_pkey'),
    )

    frequency_of_update_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency_of_update_desc: Mapped[str] = mapped_column(String(50), nullable=False)

    repeat_master: Mapped[list['RepeatMaster']] = relationship('RepeatMaster', back_populates='frequency_of_update')
    where_to_use_each_price_type: Mapped[list['WhereToUseEachPriceType']] = relationship('WhereToUseEachPriceType', back_populates='frequency_of_update')


class IncotermsMaster(Base):
    __tablename__ = 'incoterms_master'
    __table_args__ = (
        PrimaryKeyConstraint('incoterm_id', name='incoterms_master_pkey'),
        UniqueConstraint('inco_term_name', name='uk_inco_term_name')
    )

    incoterm_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inco_term_name: Mapped[str] = mapped_column(String(10), nullable=False)
    inco_term_desc: Mapped[str] = mapped_column(String(200), nullable=False)
    transport_modes_where_used: Mapped[str] = mapped_column(String(100), nullable=False)
    packaging_charges: Mapped[str] = mapped_column(String(50), nullable=False)
    loading_charges: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_to_port: Mapped[str] = mapped_column(String(50), nullable=False)
    export_duty_taxes: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_terminal_charges: Mapped[str] = mapped_column(String(50), nullable=False)
    loading_on_carriage: Mapped[str] = mapped_column(String(50), nullable=False)
    carriage_freight_charges: Mapped[str] = mapped_column(String(50), nullable=False)
    insurance: Mapped[str] = mapped_column(String(50), nullable=False)
    destination_terminal_charges: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_to_destination_charge: Mapped[str] = mapped_column(String(50), nullable=False)
    import_duty_taxes: Mapped[str] = mapped_column(String(50), nullable=False)

    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='incoterms_master')


class LocationTypeMaster(Base):
    __tablename__ = 'location_type_master'
    __table_args__ = (
        PrimaryKeyConstraint('location_type_id', name='location_type_master_pkey'),
    )

    location_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_type_desc: Mapped[str] = mapped_column(String(20), nullable=False)

    location_master: Mapped[list['LocationMaster']] = relationship('LocationMaster', back_populates='location_type')


class MaterialTypeMaster(Base):
    __tablename__ = 'material_type_master'
    __table_args__ = (
        PrimaryKeyConstraint('material_type_master_id', name='material_type_master_pkey'),
    )

    material_type_master_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_type_master_desc: Mapped[str] = mapped_column(String(255), nullable=False)

    material_master: Mapped[list['MaterialMaster']] = relationship('MaterialMaster', back_populates='material_type')


class NewsTags(Base):
    __tablename__ = 'news_tags'
    __table_args__ = (
        PrimaryKeyConstraint('news_tag_id', name='news_tags_pkey'),
    )

    news_tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_tag_description: Mapped[str] = mapped_column(String(100), nullable=False)
    news_synonyms: Mapped[str] = mapped_column(String(500), nullable=False)


class PortMaster(Base):
    __tablename__ = 'port_master'
    __table_args__ = (
        PrimaryKeyConstraint('port_id', name='port_master_pkey'),
    )

    port_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    port: Mapped[str] = mapped_column(String(100), nullable=False)
    freight_mode: Mapped[str] = mapped_column(Enum('SEA', 'AIR', 'RAIL', 'MULTI', name='freight_mode_enum'), nullable=False, server_default=text("'SEA'::freight_mode_enum"))

    ocean_freight_master: Mapped[list['OceanFreightMaster']] = relationship('OceanFreightMaster', foreign_keys='[OceanFreightMaster.destination_port_id]', back_populates='destination_port')
    ocean_freight_master_: Mapped[list['OceanFreightMaster']] = relationship('OceanFreightMaster', foreign_keys='[OceanFreightMaster.source_port_id]', back_populates='source_port')
    plant_to_port_mapping_master: Mapped[list['PlantToPortMappingMaster']] = relationship('PlantToPortMappingMaster', back_populates='port')


class PricingSourceMaster(Base):
    __tablename__ = 'pricing_source_master'
    __table_args__ = (
        PrimaryKeyConstraint('source_of_price_id', name='pricing_source_master_pkey'),
    )

    source_of_price_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_of_price_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    credentials_api_key: Mapped[Optional[str]] = mapped_column(String(255))
    user_id: Mapped[Optional[str]] = mapped_column(String(100))

    where_to_use_each_price_type: Mapped[list['WhereToUseEachPriceType']] = relationship('WhereToUseEachPriceType', back_populates='source_of_price')


class PricingTypeMaster(Base):
    __tablename__ = 'pricing_type_master'
    __table_args__ = (
        PrimaryKeyConstraint('price_type_id', name='pricing_type_master_pkey'),
    )

    price_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_type_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    source_of_price: Mapped[Optional[str]] = mapped_column(String(100))
    frequency_of_update: Mapped[Optional[str]] = mapped_column(String(50))

    where_to_use_each_price_type: Mapped[list['WhereToUseEachPriceType']] = relationship('WhereToUseEachPriceType', back_populates='price_type')


class PurchasingOrganizations(Base):
    __tablename__ = 'purchasing_organizations'
    __table_args__ = (
        PrimaryKeyConstraint('purchasing_org_id', name='purchasing_organizations_pkey'),
    )

    purchasing_org_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchasing_org_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    org_code: Mapped[Optional[str]] = mapped_column(String(10))

    company_currency_exchange_history: Mapped[list['CompanyCurrencyExchangeHistory']] = relationship('CompanyCurrencyExchangeHistory', back_populates='purchase_org')
    audit_snapshot_price_prediction_negotiation: Mapped[list['AuditSnapshotPricePredictionNegotiation']] = relationship('AuditSnapshotPricePredictionNegotiation', back_populates='purchasing_org')
    news_porg_plant_material_source_data: Mapped[list['NewsPorgPlantMaterialSourceData']] = relationship('NewsPorgPlantMaterialSourceData', back_populates='purchasing_org')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='purchasing_org')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='purchasing_org')
    tile_multiple_point_engagements: Mapped[list['TileMultiplePointEngagements']] = relationship('TileMultiplePointEngagements', back_populates='purchasing_org')
    tile_vendor_minutes_of_meeting: Mapped[list['TileVendorMinutesOfMeeting']] = relationship('TileVendorMinutesOfMeeting', back_populates='purchasing_org')


class QuoteCompare(Base):
    __tablename__ = 'quote_compare'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='quote_compare_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    material_code: Mapped[str] = mapped_column(String(50), nullable=False)
    price_per_unit: Mapped[decimal.Decimal] = mapped_column(Numeric(15, 2), nullable=False, server_default=text('0'))
    quote_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(200))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    country_of_origin: Mapped[Optional[str]] = mapped_column(String(100))
    pdf_key: Mapped[Optional[str]] = mapped_column(String(255))
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class SettingsFieldNamesInTable(Base):
    __tablename__ = 'settings_field_names_in_table'
    __table_args__ = (
        PrimaryKeyConstraint('field_name_change_id', name='settings_field_names_in_table_pkey'),
    )

    field_name_change_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    existing_field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    new_field_name: Mapped[str] = mapped_column(String(100), nullable=False)


class Tiles(Base):
    __tablename__ = 'tiles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tiles_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))


class UomConversion(Base):
    __tablename__ = 'uom_conversion'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='uom_conversion_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_uom_name: Mapped[str] = mapped_column(String(50), nullable=False)
    to_uom_name: Mapped[str] = mapped_column(String(50), nullable=False)
    what_does_it_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    conversion_factor: Mapped[decimal.Decimal] = mapped_column(Numeric(15, 6), nullable=False)
    syn: Mapped[Optional[str]] = mapped_column(String(500))


class UomMaster(Base):
    __tablename__ = 'uom_master'
    __table_args__ = (
        PrimaryKeyConstraint('uom_id', name='uom_master_pkey'),
        UniqueConstraint('uom_name', name='uk_uom_name'),
        UniqueConstraint('uom_name', name='uom_master_uom_name_key')
    )

    uom_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uom_name: Mapped[str] = mapped_column(Text, nullable=False)
    uom_symbol: Mapped[Optional[str]] = mapped_column(Text)
    measurement_type: Mapped[Optional[str]] = mapped_column(Text)
    uom_system: Mapped[Optional[str]] = mapped_column(Text)
    synonyms: Mapped[Optional[dict]] = mapped_column(JSONB, comment='Stores alternative names as a JSON array, e.g., ["kgs", "kilo"]')

    material_master: Mapped[list['MaterialMaster']] = relationship('MaterialMaster', back_populates='base_uom')
    export_data: Mapped[list['ExportData']] = relationship('ExportData', back_populates='uom_master')
    import_data: Mapped[list['ImportData']] = relationship('ImportData', back_populates='uom_master')
    price_history_data: Mapped[list['PriceHistoryData']] = relationship('PriceHistoryData', back_populates='uom_master')
    tile_cost_sheet_chemical_reaction_master_data: Mapped[list['TileCostSheetChemicalReactionMasterData']] = relationship('TileCostSheetChemicalReactionMasterData', foreign_keys='[TileCostSheetChemicalReactionMasterData.material_base_uom_id]', back_populates='material_base_uom')
    tile_cost_sheet_chemical_reaction_master_data_: Mapped[list['TileCostSheetChemicalReactionMasterData']] = relationship('TileCostSheetChemicalReactionMasterData', foreign_keys='[TileCostSheetChemicalReactionMasterData.reaction_raw_material_base_uom_id]', back_populates='reaction_raw_material_base_uom')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='uom_master')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='uom_master')


class UserMaster(Base):
    __tablename__ = 'user_master'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_master_pkey'),
    )

    user_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255))
    user_password: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[Optional[str]] = mapped_column(String)

    currency: Mapped[list['CurrencyMaster']] = relationship('CurrencyMaster', secondary='user_preference_currency', back_populates='user')
    currency_master: Mapped[list['CurrencyMaster']] = relationship('CurrencyMaster', secondary='user_currency_preference', back_populates='user_')
    location: Mapped[list['LocationMaster']] = relationship('LocationMaster', secondary='user_preferred_location', back_populates='user')
    market_research_status: Mapped[list['MarketResearchStatus']] = relationship('MarketResearchStatus', back_populates='user')
    material: Mapped[list['MaterialMaster']] = relationship('MaterialMaster', secondary='user_preferred_material', back_populates='user')
    settings_user_material_category: Mapped[list['SettingsUserMaterialCategory']] = relationship('SettingsUserMaterialCategory', back_populates='user')
    settings_user_material_category_tile_preferences: Mapped[list['SettingsUserMaterialCategoryTilePreferences']] = relationship('SettingsUserMaterialCategoryTilePreferences', back_populates='user')
    user_purchase_org: Mapped[list['UserPurchaseOrg']] = relationship('UserPurchaseOrg', back_populates='user')
    action_plans: Mapped[list['ActionPlans']] = relationship('ActionPlans', back_populates='user_master')
    demand_supply_trends: Mapped[list['DemandSupplyTrends']] = relationship('DemandSupplyTrends', foreign_keys='[DemandSupplyTrends.update_user_id]', back_populates='update_user')
    demand_supply_trends_: Mapped[list['DemandSupplyTrends']] = relationship('DemandSupplyTrends', foreign_keys='[DemandSupplyTrends.upload_user_id]', back_populates='upload_user')
    fact_pack: Mapped[list['FactPack']] = relationship('FactPack', back_populates='user_master')
    material_research_reports: Mapped[list['MaterialResearchReports']] = relationship('MaterialResearchReports', foreign_keys='[MaterialResearchReports.update_user_id]', back_populates='update_user')
    material_research_reports_: Mapped[list['MaterialResearchReports']] = relationship('MaterialResearchReports', foreign_keys='[MaterialResearchReports.upload_user_id]', back_populates='upload_user')
    porters_analysis: Mapped[list['PortersAnalysis']] = relationship('PortersAnalysis', back_populates='updated_user')
    news_porg_plant_material_source_data: Mapped[list['NewsPorgPlantMaterialSourceData']] = relationship('NewsPorgPlantMaterialSourceData', back_populates='user')
    plan_assignments: Mapped[list['PlanAssignments']] = relationship('PlanAssignments', back_populates='user')


class CompanyCurrencyExchangeHistory(Base):
    __tablename__ = 'company_currency_exchange_history'
    __table_args__ = (
        ForeignKeyConstraint(['from_currency'], ['currency_master.currency_name'], name='company_currency_exchange_history_from_currency_fkey'),
        ForeignKeyConstraint(['purchase_org_id'], ['purchasing_organizations.purchasing_org_id'], name='company_currency_exchange_history_purchase_org_id_fkey'),
        ForeignKeyConstraint(['to_currency'], ['currency_master.currency_name'], name='company_currency_exchange_history_to_currency_fkey'),
        PrimaryKeyConstraint('currency_exchange_purchase_org_id', name='company_currency_exchange_history_pkey')
    )

    currency_exchange_purchase_org_id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    date_from: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    date_to: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    multiplier: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    purchase_org_id: Mapped[Optional[int]] = mapped_column(Integer)

    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[from_currency], back_populates='company_currency_exchange_history')
    purchase_org: Mapped[Optional['PurchasingOrganizations']] = relationship('PurchasingOrganizations', back_populates='company_currency_exchange_history')
    currency_master_: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[to_currency], back_populates='company_currency_exchange_history_')


class CountryHsnCodeWiseDutyStructure(Base):
    __tablename__ = 'country_hsn_code_wise_duty_structure'
    __table_args__ = (
        ForeignKeyConstraint(['country_of_origin_all_code'], ['country_master.country_code'], name='country_hsn_code_wise_duty_stru_country_of_origin_all_code_fkey'),
        ForeignKeyConstraint(['destination_country_code'], ['country_master.country_code'], name='country_hsn_code_wise_duty_struct_destination_country_code_fkey'),
        PrimaryKeyConstraint('id', name='country_hsn_code_wise_duty_structure_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=False)
    destination_country_code: Mapped[str] = mapped_column(String(100), nullable=False)
    net_duty: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    country_of_origin_all_code: Mapped[str] = mapped_column(String(100), nullable=False)

    country_master: Mapped['CountryMaster'] = relationship('CountryMaster', foreign_keys=[country_of_origin_all_code], back_populates='country_hsn_code_wise_duty_structure')
    country_master_: Mapped['CountryMaster'] = relationship('CountryMaster', foreign_keys=[destination_country_code], back_populates='country_hsn_code_wise_duty_structure_')


class CountryTariffs(Base):
    __tablename__ = 'country_tariffs'
    __table_args__ = (
        ForeignKeyConstraint(['country_id'], ['country_master.country_id'], name='fk_tariff_country'),
        PrimaryKeyConstraint('id', name='country_tariffs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tariff_percentage: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    country: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='country_tariffs')


class CurrencyExchangeHistory(Base):
    __tablename__ = 'currency_exchange_history'
    __table_args__ = (
        ForeignKeyConstraint(['from_currency'], ['currency_master.currency_name'], name='currency_exchange_history_from_currency_fkey'),
        ForeignKeyConstraint(['to_currency'], ['currency_master.currency_name'], name='currency_exchange_history_to_currency_fkey'),
        PrimaryKeyConstraint('currency_exchange_id', name='currency_exchange_history_pkey')
    )

    currency_exchange_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    date_from: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    date_to: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    multiplier: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    purchase_org_id: Mapped[str] = mapped_column(String(20), nullable=False)

    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[from_currency], back_populates='currency_exchange_history')
    currency_master_: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[to_currency], back_populates='currency_exchange_history_')


class LocationMaster(Base):
    __tablename__ = 'location_master'
    __table_args__ = (
        ForeignKeyConstraint(['location_type_id'], ['location_type_master.location_type_id'], ondelete='RESTRICT', name='fk_location_master'),
        PrimaryKeyConstraint('location_id', name='location_master_pkey')
    )

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type_id: Mapped[Optional[int]] = mapped_column(Integer)

    location_type: Mapped[Optional['LocationTypeMaster']] = relationship('LocationTypeMaster', back_populates='location_master')
    user: Mapped[list['UserMaster']] = relationship('UserMaster', secondary='user_preferred_location', back_populates='location')
    demand_supply_summary: Mapped[list['DemandSupplySummary']] = relationship('DemandSupplySummary', back_populates='location')
    demand_supply_trends: Mapped[list['DemandSupplyTrends']] = relationship('DemandSupplyTrends', back_populates='location')
    export_data: Mapped[list['ExportData']] = relationship('ExportData', back_populates='location')
    forecast_recommendations: Mapped[list['ForecastRecommendations']] = relationship('ForecastRecommendations', back_populates='location')
    import_data: Mapped[list['ImportData']] = relationship('ImportData', back_populates='location')
    inventory_levels: Mapped[list['InventoryLevels']] = relationship('InventoryLevels', back_populates='location_')
    price_forecast_data: Mapped[list['PriceForecastData']] = relationship('PriceForecastData', back_populates='location')
    price_history_data: Mapped[list['PriceHistoryData']] = relationship('PriceHistoryData', back_populates='location')
    region_hierarchy: Mapped[list['RegionHierarchy']] = relationship('RegionHierarchy', back_populates='location')
    supplier_master: Mapped[list['SupplierMaster']] = relationship('SupplierMaster', back_populates='supplier_country')
    esg_tracker: Mapped[list['EsgTracker']] = relationship('EsgTracker', back_populates='location')
    supplier_shutdowns: Mapped[list['SupplierShutdowns']] = relationship('SupplierShutdowns', back_populates='location')
    supplier_tracking: Mapped[list['SupplierTracking']] = relationship('SupplierTracking', back_populates='location')


class MarketResearchStatus(Base):
    __tablename__ = 'market_research_status'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], ondelete='CASCADE', name='fk_user'),
        PrimaryKeyConstraint('id', name='market_research_status_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pdfkey: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    material_id: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped['UserMaster'] = relationship('UserMaster', back_populates='market_research_status')


class MaterialMaster(Base):
    __tablename__ = 'material_master'
    __table_args__ = (
        ForeignKeyConstraint(['base_uom_id'], ['uom_master.uom_id'], ondelete='RESTRICT', name='fk_base_uom'),
        ForeignKeyConstraint(['material_type_id'], ['material_type_master.material_type_master_id'], ondelete='RESTRICT', name='fk_material_type'),
        PrimaryKeyConstraint('material_id', name='material_master_pkey')
    )

    material_id: Mapped[str] = mapped_column(String(13), primary_key=True)
    material_description: Mapped[str] = mapped_column(Text, nullable=False)
    material_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'Active'::character varying"))
    base_uom_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_defined_material_desc: Mapped[Optional[str]] = mapped_column(Text)
    material_category: Mapped[Optional[str]] = mapped_column(String(50))
    cas_no: Mapped[Optional[str]] = mapped_column(String(13))
    unspsc_code: Mapped[Optional[str]] = mapped_column(String(13))
    hsn_code: Mapped[Optional[str]] = mapped_column(String(13))

    base_uom: Mapped['UomMaster'] = relationship('UomMaster', back_populates='material_master')
    material_type: Mapped['MaterialTypeMaster'] = relationship('MaterialTypeMaster', back_populates='material_master')
    user: Mapped[list['UserMaster']] = relationship('UserMaster', secondary='user_preferred_material', back_populates='material')
    action_plans: Mapped[list['ActionPlans']] = relationship('ActionPlans', back_populates='material')
    audit_snapshot_price_prediction_negotiation: Mapped[list['AuditSnapshotPricePredictionNegotiation']] = relationship('AuditSnapshotPricePredictionNegotiation', back_populates='material')
    demand_supply_summary: Mapped[list['DemandSupplySummary']] = relationship('DemandSupplySummary', back_populates='material')
    demand_supply_trends: Mapped[list['DemandSupplyTrends']] = relationship('DemandSupplyTrends', back_populates='material')
    export_data: Mapped[list['ExportData']] = relationship('ExportData', back_populates='material')
    fact_pack: Mapped[list['FactPack']] = relationship('FactPack', back_populates='material')
    forecast_recommendations: Mapped[list['ForecastRecommendations']] = relationship('ForecastRecommendations', back_populates='material')
    import_data: Mapped[list['ImportData']] = relationship('ImportData', back_populates='material')
    inventory_levels: Mapped[list['InventoryLevels']] = relationship('InventoryLevels', back_populates='material')
    material_research_reports: Mapped[list['MaterialResearchReports']] = relationship('MaterialResearchReports', back_populates='material')
    material_synonyms: Mapped[list['MaterialSynonyms']] = relationship('MaterialSynonyms', back_populates='material')
    negotiation_llm_logs: Mapped[list['NegotiationLlmLogs']] = relationship('NegotiationLlmLogs', back_populates='material')
    negotiation_recommendations: Mapped[list['NegotiationRecommendations']] = relationship('NegotiationRecommendations', back_populates='material')
    news_insights: Mapped[list['NewsInsights']] = relationship('NewsInsights', back_populates='material')
    porters_analysis: Mapped[list['PortersAnalysis']] = relationship('PortersAnalysis', back_populates='material')
    price_data_country_storage: Mapped[list['PriceDataCountryStorage']] = relationship('PriceDataCountryStorage', back_populates='material')
    price_forecast_data: Mapped[list['PriceForecastData']] = relationship('PriceForecastData', back_populates='material')
    price_history_data: Mapped[list['PriceHistoryData']] = relationship('PriceHistoryData', back_populates='material')
    procurement_plans: Mapped[list['ProcurementPlans']] = relationship('ProcurementPlans', back_populates='material')
    tile_cost_sheet_chemical_reaction_master_data: Mapped[list['TileCostSheetChemicalReactionMasterData']] = relationship('TileCostSheetChemicalReactionMasterData', back_populates='material')
    where_to_use_each_price_type: Mapped[list['WhereToUseEachPriceType']] = relationship('WhereToUseEachPriceType', back_populates='material')
    esg_tracker: Mapped[list['EsgTracker']] = relationship('EsgTracker', back_populates='material')
    joint_development_projects: Mapped[list['JointDevelopmentProjects']] = relationship('JointDevelopmentProjects', back_populates='material')
    material_supplier_general_intelligence: Mapped[list['MaterialSupplierGeneralIntelligence']] = relationship('MaterialSupplierGeneralIntelligence', back_populates='material')
    meeting_minutes: Mapped[list['MeetingMinutes']] = relationship('MeetingMinutes', back_populates='material')
    multiple_point_engagements: Mapped[list['MultiplePointEngagements']] = relationship('MultiplePointEngagements', back_populates='material')
    news_porg_plant_material_source_data: Mapped[list['NewsPorgPlantMaterialSourceData']] = relationship('NewsPorgPlantMaterialSourceData', back_populates='material')
    plant_material_purchase_org_supplier: Mapped[list['PlantMaterialPurchaseOrgSupplier']] = relationship('PlantMaterialPurchaseOrgSupplier', back_populates='material')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='material')
    quote_comparison: Mapped[list['QuoteComparison']] = relationship('QuoteComparison', back_populates='material')
    reach_tracker: Mapped[list['ReachTracker']] = relationship('ReachTracker', back_populates='material')
    supplier_shutdowns: Mapped[list['SupplierShutdowns']] = relationship('SupplierShutdowns', back_populates='material')
    supplier_tracking: Mapped[list['SupplierTracking']] = relationship('SupplierTracking', back_populates='material')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='material')
    tile_multiple_point_engagements: Mapped[list['TileMultiplePointEngagements']] = relationship('TileMultiplePointEngagements', back_populates='material')
    tile_vendor_minutes_of_meeting: Mapped[list['TileVendorMinutesOfMeeting']] = relationship('TileVendorMinutesOfMeeting', back_populates='material')
    vendor_key_information: Mapped[list['VendorKeyInformation']] = relationship('VendorKeyInformation', back_populates='material')
    vendor_wise_action_plan: Mapped[list['VendorWiseActionPlan']] = relationship('VendorWiseActionPlan', back_populates='material')


class OceanFreightMaster(Base):
    __tablename__ = 'ocean_freight_master'
    __table_args__ = (
        ForeignKeyConstraint(['destination_port_id'], ['port_master.port_id'], name='ocean_freight_master_destination_port_id_fkey'),
        ForeignKeyConstraint(['freight_cost_currency'], ['currency_master.currency_name'], name='ocean_freight_master_freight_cost_currency_fkey'),
        ForeignKeyConstraint(['source_port_id'], ['port_master.port_id'], name='ocean_freight_master_source_port_id_fkey'),
        PrimaryKeyConstraint('ocean_freight_id', name='ocean_freight_master_pkey')
    )

    ocean_freight_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_port_id: Mapped[int] = mapped_column(Integer, nullable=False)
    destination_port_id: Mapped[int] = mapped_column(Integer, nullable=False)
    freight_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    freight_cost_currency: Mapped[str] = mapped_column(String(10), nullable=False)

    destination_port: Mapped['PortMaster'] = relationship('PortMaster', foreign_keys=[destination_port_id], back_populates='ocean_freight_master')
    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', back_populates='ocean_freight_master')
    source_port: Mapped['PortMaster'] = relationship('PortMaster', foreign_keys=[source_port_id], back_populates='ocean_freight_master_')


class PurchaserPlantMaster(Base):
    __tablename__ = 'purchaser_plant_master'
    __table_args__ = (
        ForeignKeyConstraint(['base_currency_accounting'], ['currency_master.currency_name'], name='purchaser_plant_master_base_currency_accounting_fkey'),
        ForeignKeyConstraint(['plant_country_code'], ['country_master.country_code'], name='purchaser_plant_master_plant_country_code_fkey'),
        PrimaryKeyConstraint('plant_id', name='purchaser_plant_master_pkey')
    )

    plant_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    plant_country_code: Mapped[Optional[str]] = mapped_column(String(100))
    base_currency_accounting: Mapped[Optional[str]] = mapped_column(String(10))
    special_economic_zone: Mapped[Optional[str]] = mapped_column(String(5))

    currency_master: Mapped[Optional['CurrencyMaster']] = relationship('CurrencyMaster', back_populates='purchaser_plant_master')
    country_master: Mapped[Optional['CountryMaster']] = relationship('CountryMaster', back_populates='purchaser_plant_master')
    audit_snapshot_price_prediction_negotiation: Mapped[list['AuditSnapshotPricePredictionNegotiation']] = relationship('AuditSnapshotPricePredictionNegotiation', back_populates='plant')
    plant_to_port_mapping_master: Mapped[list['PlantToPortMappingMaster']] = relationship('PlantToPortMappingMaster', back_populates='plant')
    price_data_country_storage: Mapped[list['PriceDataCountryStorage']] = relationship('PriceDataCountryStorage', back_populates='plant')
    news_porg_plant_material_source_data: Mapped[list['NewsPorgPlantMaterialSourceData']] = relationship('NewsPorgPlantMaterialSourceData', back_populates='plant')
    plant_material_purchase_org_supplier: Mapped[list['PlantMaterialPurchaseOrgSupplier']] = relationship('PlantMaterialPurchaseOrgSupplier', back_populates='plant')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='plant')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='plant')
    tile_multiple_point_engagements: Mapped[list['TileMultiplePointEngagements']] = relationship('TileMultiplePointEngagements', back_populates='plant')
    tile_vendor_minutes_of_meeting: Mapped[list['TileVendorMinutesOfMeeting']] = relationship('TileVendorMinutesOfMeeting', back_populates='plant')


class RepeatMaster(Base):
    __tablename__ = 'repeat_master'
    __table_args__ = (
        ForeignKeyConstraint(['frequency_of_update_id'], ['frequency_master.frequency_of_update_id'], name='repeat_master_frequency_of_update_id_fkey'),
        PrimaryKeyConstraint('repeat_master_id', name='repeat_master_pkey')
    )

    repeat_master_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency_of_update_id: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency_of_update_desc: Mapped[str] = mapped_column(String(50), nullable=False)
    repeat_choices: Mapped[dict] = mapped_column(JSONB, nullable=False)

    frequency_of_update: Mapped['FrequencyMaster'] = relationship('FrequencyMaster', back_populates='repeat_master')


class SettingsUserMaterialCategory(Base):
    __tablename__ = 'settings_user_material_category'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], name='settings_user_material_category_user_id_fkey'),
        PrimaryKeyConstraint('user_material_category_id', name='settings_user_material_category_pkey')
    )

    user_material_category_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tile_cost_sheet_price_history_window: Mapped[str] = mapped_column(String(100), nullable=False)
    tile_cost_sheet_periods: Mapped[str] = mapped_column(String(100), nullable=False)
    tile_cost_sheet_cost_calculation: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    tile_market_research_summary_length: Mapped[Optional[str]] = mapped_column(String(50))
    material_category: Mapped[Optional[str]] = mapped_column(String(50))
    tile_news_preferred_sources: Mapped[Optional[str]] = mapped_column(String(100))
    tile_cost_sheet_forex_values: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped[Optional['UserMaster']] = relationship('UserMaster', back_populates='settings_user_material_category')


class SettingsUserMaterialCategoryTilePreferences(Base):
    __tablename__ = 'settings_user_material_category_tile_preferences'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], name='settings_user_material_category_tile_preferences_user_id_fkey'),
        PrimaryKeyConstraint('user_material_category_id', name='settings_user_material_category_tile_preferences_pkey')
    )

    user_material_category_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tile_market_research_summary_length: Mapped[str] = mapped_column(String(20), nullable=False)
    material_category: Mapped[str] = mapped_column(String(50), nullable=False)
    tile_cost_sheet_price_history_window: Mapped[int] = mapped_column(Integer, nullable=False)
    tile_cost_sheet_periods: Mapped[str] = mapped_column(String(20), nullable=False)
    tile_cost_sheet_cost_calculation: Mapped[str] = mapped_column(String(20), nullable=False)
    tile_news_preferred_sources: Mapped[Optional[str]] = mapped_column(String(100))
    tile_cost_sheet_forex_values: Mapped[Optional[str]] = mapped_column(String(20))

    user: Mapped['UserMaster'] = relationship('UserMaster', back_populates='settings_user_material_category_tile_preferences')


t_user_currency_preference = Table(
    'user_currency_preference', Base.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_preferred_currency', String(10), nullable=False),
    ForeignKeyConstraint(['user_id'], ['user_master.user_id'], name='user_currency_preference_user_id_fkey'),
    ForeignKeyConstraint(['user_preferred_currency'], ['currency_master.currency_name'], name='user_currency_preference_user_preferred_currency_fkey'),
    PrimaryKeyConstraint('user_id', name='user_currency_preference_pkey')
)


t_user_preference_currency = Table(
    'user_preference_currency', Base.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('currency_id', Integer, nullable=False),
    ForeignKeyConstraint(['currency_id'], ['currency_master.currency_id'], ondelete='CASCADE', name='fk_currency'),
    ForeignKeyConstraint(['user_id'], ['user_master.user_id'], ondelete='CASCADE', name='fk_user'),
    PrimaryKeyConstraint('user_id', name='user_preference_currency_pkey')
)


class UserPurchaseOrg(Base):
    __tablename__ = 'user_purchase_org'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], name='user_purchase_org_user_id_fkey'),
        PrimaryKeyConstraint('user_purchase_org_id', name='user_purchase_org_pkey')
    )

    user_purchase_org_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_org_id: Mapped[Optional[str]] = mapped_column(String(20))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)

    user: Mapped[Optional['UserMaster']] = relationship('UserMaster', back_populates='user_purchase_org')


class ActionPlans(Base):
    __tablename__ = 'action_plans'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['user_master.user_id'], name='fk_action_plans_created_by'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_action_plans_material_id'),
        PrimaryKeyConstraint('id', name='action_plans_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_master: Mapped['UserMaster'] = relationship('UserMaster', back_populates='action_plans')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='action_plans')
    plan_assignments: Mapped[list['PlanAssignments']] = relationship('PlanAssignments', back_populates='plan')


class AuditSnapshotPricePredictionNegotiation(Base):
    __tablename__ = 'audit_snapshot_price_prediction_negotiation'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='audit_snapshot_price_prediction_negotiation_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='audit_snapshot_price_prediction_negotiation_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='audit_snapshot_price_prediction_negotiat_purchasing_org_id_fkey'),
        PrimaryKeyConstraint('porg_plant_material_date_id', name='audit_snapshot_price_prediction_negotiation_pkey')
    )

    porg_plant_material_date_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity_utilization: Mapped[str] = mapped_column(String(20), nullable=False)
    conversion_spread: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    factors_influencing_demand: Mapped[str] = mapped_column(Text, nullable=False)
    demand_outlook: Mapped[str] = mapped_column(String(20), nullable=False)
    factors_influencing_supply: Mapped[str] = mapped_column(Text, nullable=False)
    supply_disruption: Mapped[str] = mapped_column(String(20), nullable=False)
    business_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    news_highlights: Mapped[str] = mapped_column(Text, nullable=False)
    forecasted_value_short: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    forecasted_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    forecasted_value_long: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    factors_influencing_forecast: Mapped[str] = mapped_column(Text, nullable=False)
    forecasted_average_value: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    news_insights_obj: Mapped[str] = mapped_column(Text, nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='audit_snapshot_price_prediction_negotiation')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='audit_snapshot_price_prediction_negotiation')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='audit_snapshot_price_prediction_negotiation')


class DemandSupplySummary(Base):
    __tablename__ = 'demand_supply_summary'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='demand_supply_summary_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='demand_supply_summary_material_id_fkey'),
        PrimaryKeyConstraint('id', name='demand_supply_summary_pkey'),
        UniqueConstraint('material_id', 'location_id', 'summary_date', name='unique_material_location_date'),
        Index('idx_created_at', 'created_at'),
        Index('idx_material_location', 'material_id', 'location_id'),
        Index('idx_summary_date', 'summary_date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    demand_summary: Mapped[Optional[str]] = mapped_column(Text)
    supply_summary: Mapped[Optional[str]] = mapped_column(Text)
    combined_summary: Mapped[Optional[str]] = mapped_column(Text)
    demand_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    supply_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='demand_supply_summary')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='demand_supply_summary')


class DemandSupplyTrends(Base):
    __tablename__ = 'demand_supply_trends'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='demand_supply_trends_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='demand_supply_trends_material_id_fkey'),
        ForeignKeyConstraint(['update_user_id'], ['user_master.user_id'], name='demand_supply_trends_update_user_id_fkey'),
        ForeignKeyConstraint(['upload_user_id'], ['user_master.user_id'], name='demand_supply_trends_upload_user_id_fkey'),
        PrimaryKeyConstraint('id', name='demand_supply_trends_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    upload_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_link: Mapped[Optional[str]] = mapped_column(Text)
    source_published_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    material_id: Mapped[Optional[str]] = mapped_column(String(20))
    upload_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    update_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    demand_impact: Mapped[Optional[str]] = mapped_column(Text)
    supply_impact: Mapped[Optional[str]] = mapped_column(Text)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)

    location: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='demand_supply_trends')
    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='demand_supply_trends')
    update_user: Mapped[Optional['UserMaster']] = relationship('UserMaster', foreign_keys=[update_user_id], back_populates='demand_supply_trends')
    upload_user: Mapped[Optional['UserMaster']] = relationship('UserMaster', foreign_keys=[upload_user_id], back_populates='demand_supply_trends_')


class ExportData(Base):
    __tablename__ = 'export_data'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='fk_export_location_id'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_export_material_id'),
        ForeignKeyConstraint(['uom'], ['uom_master.uom_name'], name='fk_export_uom_name'),
        PrimaryKeyConstraint('id', name='export_data_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    month_year: Mapped[str] = mapped_column(String(10), nullable=False)
    hsn_code: Mapped[Optional[str]] = mapped_column(String(20))
    price_per_quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    uom: Mapped[Optional[str]] = mapped_column(String(50))
    currency: Mapped[Optional[str]] = mapped_column(String(3), server_default=text("'USD'::character varying"))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='export_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='export_data')
    uom_master: Mapped[Optional['UomMaster']] = relationship('UomMaster', back_populates='export_data')


class FactPack(Base):
    __tablename__ = 'fact_pack'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='CASCADE', name='fk_factpack_material'),
        ForeignKeyConstraint(['uploaded_by'], ['user_master.user_id'], ondelete='SET NULL', name='fk_factpack_user'),
        PrimaryKeyConstraint('id', name='fact_pack_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_by: Mapped[Optional[int]] = mapped_column(Integer)
    ppt_link: Mapped[Optional[str]] = mapped_column(String(255))
    key_highlights: Mapped[Optional[str]] = mapped_column(Text)
    ppt_hash: Mapped[Optional[str]] = mapped_column(String(128))

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='fact_pack')
    user_master: Mapped[Optional['UserMaster']] = relationship('UserMaster', back_populates='fact_pack')


class ForecastRecommendations(Base):
    __tablename__ = 'forecast_recommendations'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], ondelete='CASCADE', onupdate='CASCADE', name='forecast_recommendations_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='CASCADE', onupdate='CASCADE', name='forecast_recommendations_material_id_fkey'),
        PrimaryKeyConstraint('id', name='forecast_recommendations_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    conservative_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    balanced_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    aggressive_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='forecast_recommendations')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='forecast_recommendations')


class ImportData(Base):
    __tablename__ = 'import_data'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='fk_import_location_id'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_import_material_id'),
        ForeignKeyConstraint(['uom'], ['uom_master.uom_name'], name='fk_import_uom_name'),
        PrimaryKeyConstraint('id', name='import_data_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    month_year: Mapped[str] = mapped_column(String(10), nullable=False)
    hsn_code: Mapped[Optional[str]] = mapped_column(String(20))
    price_per_quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    uom: Mapped[Optional[str]] = mapped_column(String(50))
    currency: Mapped[Optional[str]] = mapped_column(String(3), server_default=text("'USD'::character varying"))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='import_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='import_data')
    uom_master: Mapped[Optional['UomMaster']] = relationship('UomMaster', back_populates='import_data')


class InventoryLevels(Base):
    __tablename__ = 'inventory_levels'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], ondelete='CASCADE', name='fk_inventory_location'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='CASCADE', name='fk_inventory_material'),
        PrimaryKeyConstraint('id', name='inventory_levels_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[decimal.Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    transaction_uom: Mapped[Optional[str]] = mapped_column(String(20))

    location_: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='inventory_levels')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='inventory_levels')


class MaterialResearchReports(Base):
    __tablename__ = 'material_research_reports'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='material_research_reports_material_id_fkey'),
        ForeignKeyConstraint(['update_user_id'], ['user_master.user_id'], name='material_research_reports_update_user_id_fkey'),
        ForeignKeyConstraint(['upload_user_id'], ['user_master.user_id'], name='material_research_reports_upload_user_id_fkey'),
        PrimaryKeyConstraint('id', name='material_research_reports_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    publication: Mapped[Optional[str]] = mapped_column(String(255))
    report_link: Mapped[Optional[str]] = mapped_column(Text)
    published_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    material_id: Mapped[Optional[str]] = mapped_column(String(20))
    upload_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    update_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    takeaway: Mapped[Optional[str]] = mapped_column(Text)

    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='material_research_reports')
    update_user: Mapped[Optional['UserMaster']] = relationship('UserMaster', foreign_keys=[update_user_id], back_populates='material_research_reports')
    upload_user: Mapped[Optional['UserMaster']] = relationship('UserMaster', foreign_keys=[upload_user_id], back_populates='material_research_reports_')


class MaterialSynonyms(Base):
    __tablename__ = 'material_synonyms'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='material_synonyms_material_id_fkey'),
        PrimaryKeyConstraint('synonym_id', name='material_synonyms_pkey')
    )

    synonym_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    material_synonym: Mapped[str] = mapped_column(String(200), nullable=False)
    synonym_language: Mapped[str] = mapped_column(String(50), nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='material_synonyms')


class NegotiationLlmLogs(Base):
    __tablename__ = 'negotiation_llm_logs'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='negotiation_llm_logs_material_id_fkey'),
        PrimaryKeyConstraint('id', name='negotiation_llm_logs_pkey'),
        UniqueConstraint('material_id', 'vendor_name', 'date', name='negotiation_llm_logs_material_id_vendor_name_date_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    logs: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='negotiation_llm_logs')


class NegotiationRecommendations(Base):
    __tablename__ = 'negotiation_recommendations'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='negotiation_recommendations_material_id_fkey'),
        PrimaryKeyConstraint('id', name='negotiation_recommendations_pkey'),
        UniqueConstraint('vendor_name', 'month_start', 'material_id', name='negotiation_recommendations_vendor_name_month_start_materia_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    month_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    material_id: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy: Mapped[Optional[dict]] = mapped_column(JSONB)
    market_update: Mapped[Optional[dict]] = mapped_column(JSONB)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='negotiation_recommendations')


class NewsInsights(Base):
    __tablename__ = 'news_insights'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='news_insights_material_id_fkey'),
        PrimaryKeyConstraint('id', name='news_insights_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    published_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_link: Mapped[Optional[str]] = mapped_column(Text)
    update_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    news_tag: Mapped[Optional[str]] = mapped_column(String)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='news_insights')


class PlantToPortMappingMaster(Base):
    __tablename__ = 'plant_to_port_mapping_master'
    __table_args__ = (
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='plant_to_port_mapping_master_plant_id_fkey'),
        ForeignKeyConstraint(['port_country_code'], ['country_master.country_code'], name='plant_to_port_mapping_master_port_country_code_fkey'),
        ForeignKeyConstraint(['port_id'], ['port_master.port_id'], name='plant_to_port_mapping_master_port_id_fkey'),
        PrimaryKeyConstraint('plant_port_id', name='plant_to_port_mapping_master_pkey')
    )

    plant_port_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    plant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    port_id: Mapped[int] = mapped_column(Integer, nullable=False)
    port_name: Mapped[str] = mapped_column(String(100), nullable=False)
    port_country_code: Mapped[str] = mapped_column(String(10), nullable=False)
    preferred_port: Mapped[bool] = mapped_column(Boolean, nullable=False)

    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='plant_to_port_mapping_master')
    country_master: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='plant_to_port_mapping_master')
    port: Mapped['PortMaster'] = relationship('PortMaster', back_populates='plant_to_port_mapping_master')


class PortersAnalysis(Base):
    __tablename__ = 'porters_analysis'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='porters_analysis_material_id_fkey'),
        ForeignKeyConstraint(['updated_user_id'], ['user_master.user_id'], name='fk_porters_analysis_updated_user'),
        PrimaryKeyConstraint('id', name='porters_analysis_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    analysis_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    created_at: Mapped[Optional[datetime.date]] = mapped_column(Date, server_default=text('CURRENT_DATE'))
    updated_at: Mapped[Optional[datetime.date]] = mapped_column(Date, server_default=text('CURRENT_DATE'))
    updated_user_id: Mapped[Optional[int]] = mapped_column(Integer)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='porters_analysis')
    updated_user: Mapped[Optional['UserMaster']] = relationship('UserMaster', back_populates='porters_analysis')


class PriceDataCountryStorage(Base):
    __tablename__ = 'price_data_country_storage'
    __table_args__ = (
        ForeignKeyConstraint(['country'], ['country_master.country_name'], name='price_data_country_storage_country_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='price_data_country_storage_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='price_data_country_storage_plant_id_fkey'),
        PrimaryKeyConstraint('material_plant_id', name='price_data_country_storage_pkey')
    )

    material_plant_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    country_master: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='price_data_country_storage')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='price_data_country_storage')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='price_data_country_storage')


class PriceForecastData(Base):
    __tablename__ = 'price_forecast_data'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='fk_forecast_location'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_forecast_material'),
        PrimaryKeyConstraint('forecast_id', name='price_forecast_data_pkey'),
        UniqueConstraint('material_id', 'location_id', 'model_name', 'forecast_date', name='unique_forecast'),
        Index('idx_forecast_unique', 'material_id', 'location_id', 'model_name', 'forecast_date')
    )

    forecast_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    forecast_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    forecast_value: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    mape: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 3))
    model_details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'forecast_lambda'::character varying"))

    location: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='price_forecast_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='price_forecast_data')


class PriceHistoryData(Base):
    __tablename__ = 'price_history_data'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='price_history_data_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='price_history_data_material_id_fkey'),
        ForeignKeyConstraint(['price_currency'], ['currency_master.currency_name'], name='price_history_data_price_currency_fkey'),
        ForeignKeyConstraint(['uom'], ['uom_master.uom_name'], name='fk_price_history_uom'),
        PrimaryKeyConstraint('material_price_type_period_id', name='price_history_data_pkey')
    )

    material_price_type_period_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    period_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    period_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    price_history_source: Mapped[str] = mapped_column(String(100), nullable=False)
    price_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    uom: Mapped[Optional[str]] = mapped_column(String(50))

    location: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='price_history_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='price_history_data')
    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', back_populates='price_history_data')
    uom_master: Mapped[Optional['UomMaster']] = relationship('UomMaster', back_populates='price_history_data')


class ProcurementPlans(Base):
    __tablename__ = 'procurement_plans'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_procurement_material'),
        PrimaryKeyConstraint('id', name='procurement_plans_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    plant_code: Mapped[str] = mapped_column(String(20), nullable=False)
    opening_stock: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    safety_stock: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    currency: Mapped[Optional[str]] = mapped_column(String)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='procurement_plans')


class RegionHierarchy(Base):
    __tablename__ = 'region_hierarchy'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='region_hierarchy_location_id_fkey'),
        PrimaryKeyConstraint('synonym_id', name='region_hierarchy_pkey')
    )

    synonym_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    region_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region_synonym: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=False)

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='region_hierarchy')


class SupplierMaster(Base):
    __tablename__ = 'supplier_master'
    __table_args__ = (
        ForeignKeyConstraint(['base_currency_id'], ['currency_master.currency_id'], name='supplier_master_base_currency_id_fkey'),
        ForeignKeyConstraint(['supplier_country_id'], ['location_master.location_id'], name='supplier_master_supplier_country_id_fkey'),
        PrimaryKeyConstraint('supplier_id', name='supplier_master_pkey')
    )

    supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_plant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_status: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_country_id: Mapped[Optional[int]] = mapped_column(Integer)
    supplier_country_name: Mapped[Optional[str]] = mapped_column(String(100))
    base_currency_id: Mapped[Optional[int]] = mapped_column(Integer)
    relevant_country_region: Mapped[Optional[str]] = mapped_column(String(100))
    user_defined_supplier_desc: Mapped[Optional[str]] = mapped_column(String(200))
    supplier_duns: Mapped[Optional[str]] = mapped_column(String(50))

    base_currency: Mapped[Optional['CurrencyMaster']] = relationship('CurrencyMaster', back_populates='supplier_master')
    supplier_country: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='supplier_master')
    esg_tracker: Mapped[list['EsgTracker']] = relationship('EsgTracker', back_populates='supplier')
    joint_development_projects: Mapped[list['JointDevelopmentProjects']] = relationship('JointDevelopmentProjects', back_populates='supplier_')
    material_supplier_general_intelligence: Mapped[list['MaterialSupplierGeneralIntelligence']] = relationship('MaterialSupplierGeneralIntelligence', back_populates='supplier')
    meeting_minutes: Mapped[list['MeetingMinutes']] = relationship('MeetingMinutes', back_populates='supplier_')
    multiple_point_engagements: Mapped[list['MultiplePointEngagements']] = relationship('MultiplePointEngagements', back_populates='supplier_')
    news_porg_plant_material_source_data: Mapped[list['NewsPorgPlantMaterialSourceData']] = relationship('NewsPorgPlantMaterialSourceData', back_populates='supplier')
    plant_material_purchase_org_supplier: Mapped[list['PlantMaterialPurchaseOrgSupplier']] = relationship('PlantMaterialPurchaseOrgSupplier', back_populates='supplier')
    purchase_history_transactional_data: Mapped[list['PurchaseHistoryTransactionalData']] = relationship('PurchaseHistoryTransactionalData', back_populates='supplier')
    quote_comparison: Mapped[list['QuoteComparison']] = relationship('QuoteComparison', back_populates='supplier')
    reach_tracker: Mapped[list['ReachTracker']] = relationship('ReachTracker', back_populates='supplier')
    supplier_hierarchy: Mapped[list['SupplierHierarchy']] = relationship('SupplierHierarchy', foreign_keys='[SupplierHierarchy.parent_supplier_id]', back_populates='parent_supplier')
    supplier_hierarchy_: Mapped[list['SupplierHierarchy']] = relationship('SupplierHierarchy', foreign_keys='[SupplierHierarchy.supplier_id]', back_populates='supplier')
    supplier_shutdowns: Mapped[list['SupplierShutdowns']] = relationship('SupplierShutdowns', back_populates='supplier')
    supplier_tracking: Mapped[list['SupplierTracking']] = relationship('SupplierTracking', back_populates='supplier')
    tile_cost_sheet_historical_current_supplier: Mapped[list['TileCostSheetHistoricalCurrentSupplier']] = relationship('TileCostSheetHistoricalCurrentSupplier', back_populates='supplier')
    tile_multiple_point_engagements: Mapped[list['TileMultiplePointEngagements']] = relationship('TileMultiplePointEngagements', back_populates='supplier')
    tile_vendor_minutes_of_meeting: Mapped[list['TileVendorMinutesOfMeeting']] = relationship('TileVendorMinutesOfMeeting', back_populates='supplier')
    vendor_key_information: Mapped[list['VendorKeyInformation']] = relationship('VendorKeyInformation', back_populates='supplier')
    vendor_wise_action_plan: Mapped[list['VendorWiseActionPlan']] = relationship('VendorWiseActionPlan', back_populates='supplier')


class TileCostSheetChemicalReactionMasterData(Base):
    __tablename__ = 'tile_cost_sheet_chemical_reaction_master_data'
    __table_args__ = (
        ForeignKeyConstraint(['material_base_uom_id'], ['uom_master.uom_id'], name='tile_cost_sheet_chemical_reaction_mas_material_base_uom_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='tile_cost_sheet_chemical_reaction_master_data_material_id_fkey'),
        ForeignKeyConstraint(['reaction_raw_material_base_uom_id'], ['uom_master.uom_id'], name='tile_cost_sheet_chemical_reac_reaction_raw_material_base_u_fkey'),
        PrimaryKeyConstraint('m_cr_rrm_id', name='tile_cost_sheet_chemical_reaction_master_data_pkey')
    )

    m_cr_rrm_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    material_desc: Mapped[str] = mapped_column(String(200), nullable=False)
    chemical_reaction_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reaction_raw_material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    reaction_raw_material_desc: Mapped[str] = mapped_column(String(200), nullable=False)
    material_base_uom_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_base_uom_name: Mapped[str] = mapped_column(String(50), nullable=False)
    reaction_raw_material_base_uom_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reaction_raw_material_base_uom_name: Mapped[str] = mapped_column(String(50), nullable=False)
    reaction_raw_material_1_consumption: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    valid_from: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    reaction_raw_material_cas_no: Mapped[Optional[str]] = mapped_column(String(50))

    material_base_uom: Mapped['UomMaster'] = relationship('UomMaster', foreign_keys=[material_base_uom_id], back_populates='tile_cost_sheet_chemical_reaction_master_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='tile_cost_sheet_chemical_reaction_master_data')
    reaction_raw_material_base_uom: Mapped['UomMaster'] = relationship('UomMaster', foreign_keys=[reaction_raw_material_base_uom_id], back_populates='tile_cost_sheet_chemical_reaction_master_data_')


t_user_preferred_location = Table(
    'user_preferred_location', Base.metadata,
    Column('user_id', Integer, nullable=False),
    Column('location_id', Integer, nullable=False),
    ForeignKeyConstraint(['location_id'], ['location_master.location_id'], ondelete='CASCADE', name='fk_location'),
    ForeignKeyConstraint(['user_id'], ['user_master.user_id'], ondelete='CASCADE', name='fk_user'),
    UniqueConstraint('user_id', 'location_id', name='unique_user_location')
)


t_user_preferred_material = Table(
    'user_preferred_material', Base.metadata,
    Column('user_id', Integer, nullable=False),
    Column('material_id', String, nullable=False),
    ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='CASCADE', name='fk_material'),
    ForeignKeyConstraint(['user_id'], ['user_master.user_id'], ondelete='CASCADE', name='fk_user')
)


class WhereToUseEachPriceType(Base):
    __tablename__ = 'where_to_use_each_price_type'
    __table_args__ = (
        ForeignKeyConstraint(['frequency_of_update_id'], ['frequency_master.frequency_of_update_id'], name='where_to_use_each_price_type_frequency_of_update_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='where_to_use_each_price_type_material_id_fkey'),
        ForeignKeyConstraint(['price_type_id'], ['pricing_type_master.price_type_id'], name='where_to_use_each_price_type_price_type_id_fkey'),
        ForeignKeyConstraint(['source_of_price_id'], ['pricing_source_master.source_of_price_id'], name='where_to_use_each_price_type_source_of_price_id_fkey'),
        PrimaryKeyConstraint('porg_material_price_type_id', name='where_to_use_each_price_type_pkey')
    )

    porg_material_price_type_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    material_description: Mapped[str] = mapped_column(String(200), nullable=False)
    price_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_type_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    source_of_price_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_series_to_extract_from_source: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency_of_update_id: Mapped[int] = mapped_column(Integer, nullable=False)
    repeat_choice: Mapped[str] = mapped_column(String(100), nullable=False)
    purchasing_org_id: Mapped[Optional[str]] = mapped_column(String(20))
    data_series_pricing_market: Mapped[Optional[str]] = mapped_column(String(100))
    data_series_incoterm: Mapped[Optional[str]] = mapped_column(String(50))
    data_series_currency: Mapped[Optional[str]] = mapped_column(String(10))
    data_series_uom: Mapped[Optional[str]] = mapped_column(String(20))
    use_in_cost_sheet: Mapped[Optional[str]] = mapped_column(String(5))
    use_in_price_benchmarking: Mapped[Optional[str]] = mapped_column(String(5))
    use_in_spend_analytics: Mapped[Optional[str]] = mapped_column(String(5))
    last_updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    frequency_of_update: Mapped['FrequencyMaster'] = relationship('FrequencyMaster', back_populates='where_to_use_each_price_type')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='where_to_use_each_price_type')
    price_type: Mapped['PricingTypeMaster'] = relationship('PricingTypeMaster', back_populates='where_to_use_each_price_type')
    source_of_price: Mapped['PricingSourceMaster'] = relationship('PricingSourceMaster', back_populates='where_to_use_each_price_type')


class EsgTracker(Base):
    __tablename__ = 'esg_tracker'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='fk_esg_location'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_esg_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='fk_esg_supplier'),
        PrimaryKeyConstraint('id', name='esg_tracker_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    co2_emission_per_ton: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 3))
    certificate: Mapped[Optional[str]] = mapped_column(String(100))
    certificate_validity: Mapped[Optional[datetime.date]] = mapped_column(Date)
    quantity_purchased_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    quantity_previous_year_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    quantity_previous_to_previous_year_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    location: Mapped['LocationMaster'] = relationship('LocationMaster', back_populates='esg_tracker')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='esg_tracker')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='esg_tracker')


class JointDevelopmentProjects(Base):
    __tablename__ = 'joint_development_projects'
    __table_args__ = (
        ForeignKeyConstraint(['gmail_id'], ['emails.gmail_id'], ondelete='CASCADE', name='fk_jdp_gmail'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='RESTRICT', name='fk_jdp_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], ondelete='RESTRICT', name='fk_jdp_supplier'),
        PrimaryKeyConstraint('id', name='joint_development_projects_pkey'),
        UniqueConstraint('gmail_id', name='joint_development_projects_gmail_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier: Mapped[Optional[str]] = mapped_column(String(200))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    project: Mapped[Optional[str]] = mapped_column(Text)
    mom_link: Mapped[Optional[str]] = mapped_column(Text)
    key_takeaway: Mapped[Optional[str]] = mapped_column(Text)
    next_action_point: Mapped[Optional[str]] = mapped_column(Text)
    responsibility: Mapped[Optional[str]] = mapped_column(String(200))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    material_id: Mapped[Optional[str]] = mapped_column(String(13))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    gmail: Mapped['Emails'] = relationship('Emails', back_populates='joint_development_projects')
    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='joint_development_projects')
    supplier_: Mapped[Optional['SupplierMaster']] = relationship('SupplierMaster', back_populates='joint_development_projects')


class MaterialSupplierGeneralIntelligence(Base):
    __tablename__ = 'material_supplier_general_intelligence'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='material_supplier_general_intelligence_material_id_fkey'),
        ForeignKeyConstraint(['supplier_country_code'], ['country_master.country_code'], name='material_supplier_general_intelligen_supplier_country_code_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='material_supplier_general_intelligence_supplier_id_fkey'),
        PrimaryKeyConstraint('material_supplier_general_intelligence_id', name='material_supplier_general_intelligence_pkey')
    )

    material_supplier_general_intelligence_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier_contact_email: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier_contact_mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_country_code: Mapped[str] = mapped_column(String(100), nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='material_supplier_general_intelligence')
    country_master: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='material_supplier_general_intelligence')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='material_supplier_general_intelligence')


class MeetingMinutes(Base):
    __tablename__ = 'meeting_minutes'
    __table_args__ = (
        ForeignKeyConstraint(['gmail_id'], ['emails.gmail_id'], ondelete='CASCADE', name='fk_meeting_minutes_gmail'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='RESTRICT', name='fk_meeting_minutes_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], ondelete='RESTRICT', name='fk_meeting_minutes_supplier'),
        PrimaryKeyConstraint('id', name='meeting_minutes_pkey'),
        UniqueConstraint('gmail_id', name='meeting_minutes_gmail_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[Optional[str]] = mapped_column(String(50))
    supplier: Mapped[Optional[str]] = mapped_column(String(200))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    link_to_mom: Mapped[Optional[str]] = mapped_column(Text)
    key_takeaway: Mapped[Optional[str]] = mapped_column(Text)
    region: Mapped[Optional[str]] = mapped_column(String(100))
    material_id: Mapped[Optional[str]] = mapped_column(String(13))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    gmail: Mapped['Emails'] = relationship('Emails', back_populates='meeting_minutes')
    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='meeting_minutes')
    supplier_: Mapped[Optional['SupplierMaster']] = relationship('SupplierMaster', back_populates='meeting_minutes')


class MultiplePointEngagements(Base):
    __tablename__ = 'multiple_point_engagements'
    __table_args__ = (
        ForeignKeyConstraint(['gmail_id'], ['emails.gmail_id'], ondelete='CASCADE', name='fk_mpe_gmail'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='RESTRICT', name='fk_mpe_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], ondelete='RESTRICT', name='fk_mpe_supplier'),
        PrimaryKeyConstraint('id', name='multiple_point_engagements_pkey'),
        UniqueConstraint('gmail_id', name='multiple_point_engagements_gmail_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[Optional[str]] = mapped_column(String(50))
    supplier: Mapped[Optional[str]] = mapped_column(String(200))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    event: Mapped[Optional[str]] = mapped_column(Text)
    mom_link: Mapped[Optional[str]] = mapped_column(Text)
    key_takeaway: Mapped[Optional[str]] = mapped_column(Text)
    photos_link: Mapped[Optional[str]] = mapped_column(Text)
    region: Mapped[Optional[str]] = mapped_column(String(100))
    material_id: Mapped[Optional[str]] = mapped_column(String(13))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    gmail: Mapped['Emails'] = relationship('Emails', back_populates='multiple_point_engagements')
    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='multiple_point_engagements')
    supplier_: Mapped[Optional['SupplierMaster']] = relationship('SupplierMaster', back_populates='multiple_point_engagements')


class NewsPorgPlantMaterialSourceData(Base):
    __tablename__ = 'news_porg_plant_material_source_data'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='news_porg_plant_material_source_data_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='news_porg_plant_material_source_data_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='news_porg_plant_material_source_data_purchasing_org_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='news_porg_plant_material_source_data_supplier_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], name='news_porg_plant_material_source_data_user_id_fkey'),
        PrimaryKeyConstraint('news_porg_plant_material_source_data_id', name='news_porg_plant_material_source_data_pkey')
    )

    news_porg_plant_material_source_data_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_category: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    actual_news: Mapped[str] = mapped_column(Text, nullable=False)
    ai_created_impact_demand_supply: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_created_impact_summarized: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_updates_summary: Mapped[str] = mapped_column(String(200), nullable=False)
    reliability_of_news: Mapped[str] = mapped_column(String(100), nullable=False)
    news_tags: Mapped[dict] = mapped_column(JSON, nullable=False)
    date_of_publication: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    key_takeaway: Mapped[str] = mapped_column(String(500), nullable=False)
    user_update_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='news_porg_plant_material_source_data')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='news_porg_plant_material_source_data')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='news_porg_plant_material_source_data')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='news_porg_plant_material_source_data')
    user: Mapped['UserMaster'] = relationship('UserMaster', back_populates='news_porg_plant_material_source_data')


class PlanAssignments(Base):
    __tablename__ = 'plan_assignments'
    __table_args__ = (
        ForeignKeyConstraint(['plan_id'], ['action_plans.id'], ondelete='CASCADE', name='fk_plan_assignments_plan_id'),
        ForeignKeyConstraint(['user_id'], ['user_master.user_id'], ondelete='CASCADE', name='fk_plan_assignments_user_id'),
        PrimaryKeyConstraint('id', name='plan_assignments_pkey'),
        UniqueConstraint('plan_id', 'user_id', name='plan_assignments_plan_id_user_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'Pending'::character varying"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    attachment_url: Mapped[Optional[str]] = mapped_column(Text)

    plan: Mapped['ActionPlans'] = relationship('ActionPlans', back_populates='plan_assignments')
    user: Mapped['UserMaster'] = relationship('UserMaster', back_populates='plan_assignments')


class PlantMaterialPurchaseOrgSupplier(Base):
    __tablename__ = 'plant_material_purchase_org_supplier'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='plant_material_purchase_org_supplier_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='plant_material_purchase_org_supplier_plant_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='plant_material_purchase_org_supplier_supplier_id_fkey'),
        PrimaryKeyConstraint('porg_plant_material_id', name='plant_material_purchase_org_supplier_pkey')
    )

    porg_plant_material_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    plant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    purchasing_org_id: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_plant: Mapped[str] = mapped_column(String(200), nullable=False)
    material_name: Mapped[Optional[str]] = mapped_column(String(200))
    user_id: Mapped[Optional[str]] = mapped_column(String(100))
    valid_from: Mapped[Optional[datetime.date]] = mapped_column(Date)
    valid_to: Mapped[Optional[datetime.date]] = mapped_column(Date)
    user_purchase_org_id: Mapped[Optional[int]] = mapped_column(Integer)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='plant_material_purchase_org_supplier')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='plant_material_purchase_org_supplier')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='plant_material_purchase_org_supplier')


class PurchaseHistoryTransactionalData(Base):
    __tablename__ = 'purchase_history_transactional_data'
    __table_args__ = (
        ForeignKeyConstraint(['currency_of_po'], ['currency_master.currency_name'], name='purchase_history_transactional_data_currency_of_po_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='purchase_history_transactional_data_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='purchase_history_transactional_data_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='purchase_history_transactional_data_purchasing_org_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='purchase_history_transactional_data_supplier_id_fkey'),
        ForeignKeyConstraint(['uom'], ['uom_master.uom_name'], name='purchase_history_transactional_data_uom_fkey'),
        PrimaryKeyConstraint('purchase_transaction_id', name='purchase_history_transactional_data_pkey')
    )

    purchase_transaction_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    po_number: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    currency_of_po: Mapped[str] = mapped_column(String(10), nullable=False)
    uom: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost_per_uom: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(100), nullable=False)
    freight_terms: Mapped[str] = mapped_column(String(100), nullable=False)
    transaction_posting_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    buyer_name: Mapped[Optional[str]] = mapped_column(String(155))

    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', back_populates='purchase_history_transactional_data')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='purchase_history_transactional_data')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='purchase_history_transactional_data')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='purchase_history_transactional_data')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='purchase_history_transactional_data')
    uom_master: Mapped['UomMaster'] = relationship('UomMaster', back_populates='purchase_history_transactional_data')


class QuoteComparison(Base):
    __tablename__ = 'quote_comparison'
    __table_args__ = (
        ForeignKeyConstraint(['country_id'], ['country_master.country_id'], name='fk_quote_country'),
        ForeignKeyConstraint(['currency_id'], ['currency_master.currency_id'], name='fk_quote_currency'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_quote_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='fk_quote_supplier'),
        PrimaryKeyConstraint('id', name='quote_comparison_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_unit: Mapped[decimal.Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency_id: Mapped[int] = mapped_column(Integer, nullable=False)
    country_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quote_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    pdf_key: Mapped[Optional[str]] = mapped_column(String(255))
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    country: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='quote_comparison')
    currency: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', back_populates='quote_comparison')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='quote_comparison')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='quote_comparison')


class ReachTracker(Base):
    __tablename__ = 'reach_tracker'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='fk_reach_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='fk_reach_supplier'),
        PrimaryKeyConstraint('id', name='reach_tracker_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_band: Mapped[Optional[str]] = mapped_column(String(255))
    coverage_letter: Mapped[Optional[str]] = mapped_column(String(255))
    eu_sds: Mapped[Optional[str]] = mapped_column(String(255))
    certificate_type: Mapped[Optional[str]] = mapped_column(String(50))
    quantity_purchased_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    quantity_previous_year_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    quantity_previous_to_previous_year_tons: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    cover_letter_link: Mapped[Optional[str]] = mapped_column(String(255))
    eu_sds_link: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='reach_tracker')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='reach_tracker')


class SupplierHierarchy(Base):
    __tablename__ = 'supplier_hierarchy'
    __table_args__ = (
        ForeignKeyConstraint(['parent_supplier_id'], ['supplier_master.supplier_id'], name='supplier_hierarchy_parent_supplier_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='supplier_hierarchy_supplier_id_fkey'),
        PrimaryKeyConstraint('supplier_hierarchy_id', name='supplier_hierarchy_pkey')
    )

    supplier_hierarchy_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)

    parent_supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', foreign_keys=[parent_supplier_id], back_populates='supplier_hierarchy')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', foreign_keys=[supplier_id], back_populates='supplier_hierarchy_')


class SupplierShutdowns(Base):
    __tablename__ = 'supplier_shutdowns'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='supplier_shutdowns_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='supplier_shutdowns_material_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='supplier_shutdowns_supplier_id_fkey'),
        PrimaryKeyConstraint('id', name='supplier_shutdowns_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    shutdown_from: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    shutdown_to: Mapped[Optional[datetime.date]] = mapped_column(Date)
    impact: Mapped[Optional[str]] = mapped_column(Text)
    key_takeaway: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_link: Mapped[Optional[str]] = mapped_column(Text)
    published_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    upload_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    upload_user_id: Mapped[Optional[int]] = mapped_column(Integer)

    location: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='supplier_shutdowns')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='supplier_shutdowns')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='supplier_shutdowns')


class SupplierTracking(Base):
    __tablename__ = 'supplier_tracking'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location_master.location_id'], name='supplier_tracking_location_id_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='supplier_tracking_material_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='supplier_tracking_supplier_id_fkey'),
        PrimaryKeyConstraint('id', name='supplier_tracking_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    event_title: Mapped[str] = mapped_column(String(500), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    event_description: Mapped[Optional[str]] = mapped_column(Text)
    key_takeaway: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_link: Mapped[Optional[str]] = mapped_column(Text)
    published_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)

    location: Mapped[Optional['LocationMaster']] = relationship('LocationMaster', back_populates='supplier_tracking')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='supplier_tracking')
    supplier: Mapped[Optional['SupplierMaster']] = relationship('SupplierMaster', back_populates='supplier_tracking')


class TileCostSheetHistoricalCurrentSupplier(Base):
    __tablename__ = 'tile_cost_sheet_historical_current_supplier'
    __table_args__ = (
        ForeignKeyConstraint(['country_of_origin'], ['country_master.country_name'], name='tile_cost_sheet_historical_current_suppl_country_of_origin_fkey'),
        ForeignKeyConstraint(['currency_cost_factory_gate'], ['currency_master.currency_name'], name='tile_cost_sheet_historical_curr_currency_cost_factory_gate_fkey'),
        ForeignKeyConstraint(['currency_cost_given_quote'], ['currency_master.currency_name'], name='tile_cost_sheet_historical_curre_currency_cost_given_quote_fkey'),
        ForeignKeyConstraint(['incoterms'], ['incoterms_master.inco_term_name'], name='tile_cost_sheet_historical_current_supplier_incoterms_fkey'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='tile_cost_sheet_historical_current_supplier_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='tile_cost_sheet_historical_current_supplier_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='tile_cost_sheet_historical_current_suppl_purchasing_org_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='tile_cost_sheet_historical_current_supplier_supplier_id_fkey'),
        ForeignKeyConstraint(['uom_of_quote'], ['uom_master.uom_name'], name='tile_cost_sheet_historical_current_supplier_uom_of_quote_fkey'),
        PrimaryKeyConstraint('porg_plant_material_supplier_date', name='tile_cost_sheet_historical_current_supplier_pkey')
    )

    porg_plant_material_supplier_date: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_quote: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    incoterms: Mapped[str] = mapped_column(String(10), nullable=False)
    uom_of_quote: Mapped[str] = mapped_column(String(20), nullable=False)
    cost_at_factory_gate: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_cost_factory_gate: Mapped[str] = mapped_column(String(10), nullable=False)
    cost_given_in_quote: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_cost_given_quote: Mapped[str] = mapped_column(String(10), nullable=False)
    credit_terms_days: Mapped[int] = mapped_column(Integer, nullable=False)
    country_of_origin: Mapped[str] = mapped_column(String(100), nullable=False)

    country_master: Mapped['CountryMaster'] = relationship('CountryMaster', back_populates='tile_cost_sheet_historical_current_supplier')
    currency_master: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[currency_cost_factory_gate], back_populates='tile_cost_sheet_historical_current_supplier')
    currency_master_: Mapped['CurrencyMaster'] = relationship('CurrencyMaster', foreign_keys=[currency_cost_given_quote], back_populates='tile_cost_sheet_historical_current_supplier_')
    incoterms_master: Mapped['IncotermsMaster'] = relationship('IncotermsMaster', back_populates='tile_cost_sheet_historical_current_supplier')
    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='tile_cost_sheet_historical_current_supplier')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='tile_cost_sheet_historical_current_supplier')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='tile_cost_sheet_historical_current_supplier')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='tile_cost_sheet_historical_current_supplier')
    uom_master: Mapped['UomMaster'] = relationship('UomMaster', back_populates='tile_cost_sheet_historical_current_supplier')


class TileMultiplePointEngagements(Base):
    __tablename__ = 'tile_multiple_point_engagements'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='tile_multiple_point_engagements_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='tile_multiple_point_engagements_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='tile_multiple_point_engagements_purchasing_org_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='tile_multiple_point_engagements_supplier_id_fkey'),
        PrimaryKeyConstraint('porg_plant_material_supplier_date', name='tile_multiple_point_engagements_pkey')
    )

    porg_plant_material_supplier_date: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_meeting: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    reference_email_document_id: Mapped[str] = mapped_column(String(50), nullable=False)
    media_link: Mapped[str] = mapped_column(String(500), nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='tile_multiple_point_engagements')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='tile_multiple_point_engagements')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='tile_multiple_point_engagements')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='tile_multiple_point_engagements')


class TileVendorMinutesOfMeeting(Base):
    __tablename__ = 'tile_vendor_minutes_of_meeting'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], name='tile_vendor_minutes_of_meeting_material_id_fkey'),
        ForeignKeyConstraint(['plant_id'], ['purchaser_plant_master.plant_id'], name='tile_vendor_minutes_of_meeting_plant_id_fkey'),
        ForeignKeyConstraint(['purchasing_org_id'], ['purchasing_organizations.purchasing_org_id'], name='tile_vendor_minutes_of_meeting_purchasing_org_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], name='tile_vendor_minutes_of_meeting_supplier_id_fkey'),
        PrimaryKeyConstraint('porg_plant_material_supplier_date', name='tile_vendor_minutes_of_meeting_pkey')
    )

    porg_plant_material_supplier_date: Mapped[str] = mapped_column(String(50), primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(20), nullable=False)
    purchasing_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_meeting: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    reference_email_document_id: Mapped[str] = mapped_column(String(50), nullable=False)
    media_link: Mapped[str] = mapped_column(String(500), nullable=False)

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='tile_vendor_minutes_of_meeting')
    plant: Mapped['PurchaserPlantMaster'] = relationship('PurchaserPlantMaster', back_populates='tile_vendor_minutes_of_meeting')
    purchasing_org: Mapped['PurchasingOrganizations'] = relationship('PurchasingOrganizations', back_populates='tile_vendor_minutes_of_meeting')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='tile_vendor_minutes_of_meeting')


class VendorKeyInformation(Base):
    __tablename__ = 'vendor_key_information'
    __table_args__ = (
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='CASCADE', name='fk_vendor_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], ondelete='CASCADE', name='fk_vendor_supplier'),
        PrimaryKeyConstraint('id', name='vendor_key_information_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_site: Mapped[Optional[str]] = mapped_column(String(150))
    capacity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(15, 2))
    capacity_expansion_plans: Mapped[Optional[str]] = mapped_column(Text)
    fta_benefit: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    material: Mapped['MaterialMaster'] = relationship('MaterialMaster', back_populates='vendor_key_information')
    supplier: Mapped['SupplierMaster'] = relationship('SupplierMaster', back_populates='vendor_key_information')


class VendorWiseActionPlan(Base):
    __tablename__ = 'vendor_wise_action_plan'
    __table_args__ = (
        ForeignKeyConstraint(['gmail_id'], ['emails.gmail_id'], ondelete='CASCADE', name='fk_vendor_action_gmail'),
        ForeignKeyConstraint(['material_id'], ['material_master.material_id'], ondelete='RESTRICT', name='fk_vendor_action_material'),
        ForeignKeyConstraint(['supplier_id'], ['supplier_master.supplier_id'], ondelete='RESTRICT', name='fk_vendor_action_supplier'),
        PrimaryKeyConstraint('id', name='vendor_wise_action_plan_pkey'),
        UniqueConstraint('gmail_id', 'open_po', name='vendor_wise_action_plan_gmail_id_open_po_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String(255), nullable=False)
    open_po: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(200))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    pending_quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    schedule: Mapped[Optional[datetime.date]] = mapped_column(Date)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    material_id: Mapped[Optional[str]] = mapped_column(String(13))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    gmail: Mapped['Emails'] = relationship('Emails', back_populates='vendor_wise_action_plan')
    material: Mapped[Optional['MaterialMaster']] = relationship('MaterialMaster', back_populates='vendor_wise_action_plan')
    supplier: Mapped[Optional['SupplierMaster']] = relationship('SupplierMaster', back_populates='vendor_wise_action_plan')
