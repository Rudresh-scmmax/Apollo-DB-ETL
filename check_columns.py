import pandas as pd
try:
    xl = pd.ExcelFile('export.xlsx')
    sheet = 'user_preference_currency'
    if sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet, nrows=0)
        print(f"Columns in {sheet}: {list(df.columns)}")
    else:
        print(f"{sheet}: Not found")
except Exception as e:
    print(f"Error: {e}")
