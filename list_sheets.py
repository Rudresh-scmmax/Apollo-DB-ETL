import pandas as pd
try:
    xl = pd.ExcelFile('export.xlsx')
    with open('sheet_names.txt', 'w') as f:
        for sheet in xl.sheet_names:
            f.write(sheet + '\n')
    print("Sheet names written to sheet_names.txt")
except Exception as e:
    print(f"Error: {e}")
