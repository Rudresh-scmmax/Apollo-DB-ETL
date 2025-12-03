"""
Add missing MT (Metric Ton) UOM to uom_master Excel sheet.
This will fix the export_data FK violations.
"""
import pandas as pd
import openpyxl

# Read the Excel file
excel_path = 'export.xlsx'
xl = pd.ExcelFile(excel_path)

# Read uom_master sheet
uom_df = pd.read_excel(excel_path, sheet_name='uom_master')

print(f"Current UOM count: {len(uom_df)}")
print(f"Max uom_id: {uom_df['uom_id'].max()}")

# Check if MT already exists
if 'MT' in uom_df['uom_name'].values:
    print("MT already exists in uom_master!")
else:
    print("\nAdding MT (Metric Ton) to uom_master...")
    
    # Create new row for MT
    new_uom = {
        'uom_id': int(uom_df['uom_id'].max()) + 1,
        'uom_name': 'MT',
        'uom_symbol': 'MT',
        'measurement_type': 'Weight',
        'uom_system': 'Metric',
        'synonyms': '["Metric Ton", "Tonne", "t"]'  # Valid JSON
    }
    
    # Add to dataframe
    uom_df = pd.concat([uom_df, pd.DataFrame([new_uom])], ignore_index=True)
    
    print(f"New UOM count: {len(uom_df)}")
    
    # Write back to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        uom_df.to_excel(writer, sheet_name='uom_master', index=False)
    
    print("✓ MT added to uom_master sheet in export.xlsx")
    print("\nNew UOM details:")
    print(uom_df[uom_df['uom_name'] == 'MT'])
