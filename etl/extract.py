from __future__ import annotations

import pandas as pd


def read_sheet(excel_path: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')


