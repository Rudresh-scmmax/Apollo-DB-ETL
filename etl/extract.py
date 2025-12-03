from __future__ import annotations

import pandas as pd


def find_sheet_name(excel_path: str, requested_name: str) -> str:
    """
    Find sheet name in Excel file with case-insensitive matching.
    Handles all case variations: Currency_Master, currency_master, CURRENCY_MASTER, etc.
    Also handles spaces vs underscores: "UoM Master" vs "uom_master"
    Returns the actual sheet name from the file, or raises ValueError if not found.
    """
    xl = pd.ExcelFile(excel_path, engine='openpyxl')
    sheet_names = xl.sheet_names
    
    # Try exact match first (fastest)
    if requested_name in sheet_names:
        return requested_name
    
    # Normalize requested name: lowercase, strip whitespace
    requested_normalized = requested_name.lower().strip()
    
    # Try case-insensitive exact match (handles: Currency_Master -> currency_master)
    for actual_name in sheet_names:
        if actual_name.lower().strip() == requested_normalized:
            return actual_name
    
    # Try with space/underscore normalization (handles: "UoM Master" vs "uom_master")
    # Normalize both by replacing underscores/hyphens with spaces, then lowercase
    requested_space_normalized = requested_normalized.replace('_', ' ').replace('-', ' ').strip()
    for actual_name in sheet_names:
        actual_space_normalized = actual_name.lower().strip().replace('_', ' ').replace('-', ' ').strip()
        if actual_space_normalized == requested_space_normalized:
            return actual_name
    
    # Try with underscore normalization (handles: "UoM Master" -> "uom_master")
    requested_underscore_normalized = requested_space_normalized.replace(' ', '_')
    for actual_name in sheet_names:
        actual_underscore_normalized = actual_name.lower().strip().replace(' ', '_').replace('-', '_')
        if actual_underscore_normalized == requested_underscore_normalized:
            return actual_name
    
    # Try truncated match (Excel has 31-character limit for sheet names)
    # This handles cases like "tile_cost_sheet_chemical_reaction_master_data" -> "tile_cost_sheet_chemical_reacti"
    if len(requested_name) > 31:
        requested_truncated = requested_name[:31]
        for actual_name in sheet_names:
            if actual_name == requested_truncated or actual_name.lower() == requested_truncated.lower():
                return actual_name
    
    # Try partial match for truncated names (match first 20 chars)
    # This helps when the sheet name was truncated in Excel
    requested_prefix = requested_normalized[:20]
    for actual_name in sheet_names:
        if actual_name.lower().startswith(requested_prefix) and len(actual_name) <= 31:
            # Found a potential truncated match
            # Verify it's a reasonable match (at least 80% of the name matches)
            if len(requested_name) > 31 and actual_name.lower().startswith(requested_normalized[:25]):
                return actual_name
    
    # Not found - provide helpful error message with available sheets
    # Show first few matches that are close (for debugging)
    available_str = ', '.join(sheet_names[:20])
    if len(sheet_names) > 20:
        available_str += f', ... (and {len(sheet_names) - 20} more)'
    
    # Try to find close matches for better error message
    close_matches = []
    for actual_name in sheet_names:
        if requested_normalized in actual_name.lower() or actual_name.lower() in requested_normalized:
            close_matches.append(actual_name)
        if len(close_matches) >= 5:
            break
    
    error_msg = f"Worksheet named '{requested_name}' not found."
    if close_matches:
        error_msg += f" Close matches: {', '.join(close_matches[:5])}."
    error_msg += f" Available sheets: {available_str}"
    raise ValueError(error_msg)


def read_sheet(excel_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Read Excel sheet with case-insensitive matching.
    """
    actual_sheet_name = find_sheet_name(excel_path, sheet_name)
    return pd.read_excel(excel_path, sheet_name=actual_sheet_name, engine='openpyxl')


