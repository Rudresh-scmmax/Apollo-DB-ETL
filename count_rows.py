import pandas as pd
try:
    xl = pd.ExcelFile('export.xlsx')
    sheets = ['material_master', 'uom_master', 'currency_master', 'location_master', 'purchaser_plant_master']
    for sheet in sheets:
        if sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet)
            print(f"{sheet}: {len(df)} rows")
        else:
            print(f"{sheet}: Not found")
except Exception as e:
    print(f"Error: {e}")
