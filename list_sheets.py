import pandas as pd

xl = pd.ExcelFile('export.xlsx')
print(f"Total sheets: {len(xl.sheet_names)}\n")
for i, sheet in enumerate(sorted(xl.sheet_names), 1):
    print(f"{i:3d}. {sheet}")
