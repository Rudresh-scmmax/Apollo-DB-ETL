from __future__ import annotations

import os
import re
from datetime import datetime
from typing import List, Dict

import pandas as pd


def translate_technical_error_to_business(error_msg: str, table_name: str) -> str:
    """Translate technical database errors into business-friendly language."""
    
    # Foreign Key Violations
    if "ForeignKeyViolation" in error_msg:
        fk_match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\) is not present in table "([^"]+)"', error_msg)
        if fk_match:
            column, value, ref_table = fk_match.groups()
            return f"Missing Reference Data: The value '{value}' in column '{column}' does not exist in the {ref_table.replace('_', ' ').title()} table. Please ensure this value exists in the reference table first."
    
    # Missing Column Errors
    if "UndefinedColumn" in error_msg:
        col_match = re.search(r'column "([^"]+)" of relation "[^"]+" does not exist', error_msg)
        if col_match:
            column = col_match.group(1)
            return f"Column Mismatch: The Excel sheet has a column '{column}' that doesn't match the database structure. Please check the column names in your Excel file."
    
    # NOT NULL Violations
    if "NotNullViolation" in error_msg:
        null_match = re.search(r'null value in column "([^"]+)"', error_msg)
        if null_match:
            column = null_match.group(1)
            return f"Missing Required Data: Column '{column}' cannot be empty. Please provide values for all rows in this column."
    
    # JSON Format Errors
    if "InvalidTextRepresentation" in error_msg and "json" in error_msg.lower():
        return f"Data Format Issue: Some values are not in the correct format. Text values that should be lists need to be properly formatted."
    
    # Numeric Format Errors
    if "InvalidTextRepresentation" in error_msg and ("numeric" in error_msg or "integer" in error_msg):
        return f"Number Format Issue: Some values cannot be converted to numbers. Please check for special characters, text in number fields, or scientific notation."
    
    # Date Format Errors
    if "OutOfBoundsDatetime" in error_msg or "invalid input syntax for type date" in error_msg:
        return f"Date Format Issue: Some date values are invalid or out of range. Please check date formats and extreme dates like '9999-12-31'."
    
    # Duplicate Key Errors
    if "CardinalityViolation" in error_msg:
        return f"Duplicate Records: There are duplicate entries for the same key. Please remove duplicate rows from your Excel file."
    
    # Generic fallback
    return f"Data Issue: There was a problem loading data into {table_name.replace('_', ' ').title()}. Please check the data format and required fields."


class RunReporter:
    def __init__(self, base_dir: str, run_id: str):
        self.base_dir = base_dir
        self.run_id = run_id
        self.run_dir = os.path.join(base_dir, run_id)
        os.makedirs(self.run_dir, exist_ok=True)
        self.rows: List[dict] = []
        self.summary_path = os.path.join(self.run_dir, 'summary.html')
        self.business_issues: List[Dict] = []
        self.missing_materials_data = {}

    def record_table(self, sheet: str, table: str, read_rows: int, valid_rows: int, rejected_rows: int, inserted: int, updated: int, reasons: List[str]):
        self.rows.append({
            'sheet': sheet,
            'table': table,
            'read_rows': read_rows,
            'valid_rows': valid_rows,
            'rejected_rows': rejected_rows,
            'inserted': inserted,
            'updated': updated,
            'notes': '; '.join(reasons) if reasons else ''
        })
        
        # If there are rejected rows with specific reasons, add business-friendly explanations
        if rejected_rows > 0 and reasons:
            for reason in reasons:
                business_reason = self._translate_rejection_reason(reason, table)
                self.business_issues.append({
                    'sheet': sheet,
                    'table': table,
                    'issue': business_reason,
                    'action_needed': self._get_rejection_action(reason)
                })
    
    def _translate_rejection_reason(self, reason: str, table: str) -> str:
        """Translate rejection reasons to business language."""
        if "Missing required data in columns" in reason:
            # Extract column names
            col_match = re.search(r"Missing required data in columns: \[([^\]]+)\]", reason)
            if col_match:
                columns = col_match.group(1).replace("'", "").replace('"', '')
                return f"Missing Required Data: Some rows are missing values in the '{columns}' column(s)."
        
        if "Type coercion failed" in reason:
            return f"Data Format Issue: Some values are in the wrong format and cannot be converted to the required data type."
            
        return f"Data Quality Issue: {reason}"
    
    def _get_rejection_action(self, reason: str) -> str:
        """Get specific actions for rejected rows."""
        if "Missing required data" in reason:
            return "Action Required: Fill in the missing required values in your Excel file."
        elif "Type coercion failed" in reason:
            return "Action Required: Check data formats - ensure numbers are numeric, dates are valid, etc."
        else:
            return "Action Required: Review the rejected rows CSV file for specific issues."

    def record_error(self, sheet: str, table: str, error: str):
        # Store both technical and business-friendly version
        business_error = translate_technical_error_to_business(error, table)
        
        self.rows.append({
            'sheet': sheet,
            'table': table,
            'read_rows': 0,
            'valid_rows': 0,
            'rejected_rows': 0,
            'inserted': 0,
            'updated': 0,
            'notes': f'ERROR: {error}',
            'business_error': business_error
        })
        
        # Track business issues separately for cleaner reporting
        self.business_issues.append({
            'sheet': sheet,
            'table': table,
            'issue': business_error,
            'action_needed': self._get_action_needed(error, table)
        })

    def write_rejected(self, sheet: str, rejected_df: pd.DataFrame):
        if rejected_df is not None and not rejected_df.empty:
            # Ensure directory exists before writing
            os.makedirs(self.run_dir, exist_ok=True)
            path = os.path.join(self.run_dir, f'rejected_{sheet}.csv')
            try:
                rejected_df.to_csv(path, index=False)
            except Exception as e:
                # If directory creation failed, try again
                os.makedirs(self.run_dir, exist_ok=True)
                rejected_df.to_csv(path, index=False)
    
    def add_missing_materials(self, missing_materials_data: dict) -> None:
        """Add missing materials data to be included in the report."""
        self.missing_materials_data = missing_materials_data
    
    def _get_action_needed(self, error: str, table: str) -> str:
        """Provide specific actionable steps for each error type."""
        if "ForeignKeyViolation" in error:
            return "Action Required: Load the referenced table first, or verify the reference values exist."
        elif "UndefinedColumn" in error:
            return "Action Required: Check your Excel column headers and ensure they match the expected format."
        elif "NotNullViolation" in error:
            return "Action Required: Fill in all required fields - no empty cells allowed in this column."
        elif "InvalidTextRepresentation" in error and "numeric" in error:
            return "Action Required: Check number fields for text, special characters, or scientific notation."
        elif "OutOfBoundsDatetime" in error:
            return "Action Required: Review date formats and replace extreme dates like '9999-12-31' with valid dates."
        elif "CardinalityViolation" in error:
            return "Action Required: Remove duplicate rows with the same ID/key values."
        else:
            return "Action Required: Review the data format and contact the system administrator if needed."

    def finalize(self):
        # Create business-friendly HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>APOLLO ETL Run Report - {self.run_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .success {{ color: green; font-weight: bold; }}
                .error {{ color: red; font-weight: bold; }}
                .warning {{ color: orange; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>APOLLO Data Load Report</h1>
                <p><strong>Run ID:</strong> {self.run_id}</p>
                <p><strong>Generated:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Deduplicate rows - merge entries with same sheet/table combination
        # Keep the entry with most data (higher read_rows, inserted, updated, or rejected)
        deduplicated_rows = {}
        for row in self.rows:
            key = (row.get('sheet', ''), row.get('table', ''))
            if key not in deduplicated_rows:
                deduplicated_rows[key] = row
            else:
                existing = deduplicated_rows[key]
                existing_activity = existing.get('read_rows', 0) + existing.get('inserted', 0) + existing.get('updated', 0) + existing.get('rejected_rows', 0)
                new_activity = row.get('read_rows', 0) + row.get('inserted', 0) + row.get('updated', 0) + row.get('rejected_rows', 0)
                if new_activity > existing_activity:
                    deduplicated_rows[key] = row
                elif new_activity == existing_activity:
                    # Same activity - merge notes if different
                    existing_notes = existing.get('notes', '')
                    new_notes = row.get('notes', '')
                    if new_notes and new_notes not in existing_notes:
                        if existing_notes:
                            existing['notes'] = f"{existing_notes}; {new_notes}"
                        else:
                            existing['notes'] = new_notes
        
        # Calculate totals from deduplicated rows
        unique_rows = list(deduplicated_rows.values())
        total_read = sum(row.get('read_rows', 0) for row in unique_rows)
        total_valid = sum(row.get('valid_rows', 0) for row in unique_rows)
        total_rejected = sum(row.get('rejected_rows', 0) for row in unique_rows)
        total_inserted = sum(row.get('inserted', 0) for row in unique_rows)
        total_updated = sum(row.get('updated', 0) for row in unique_rows)
        
        # Overall status
        if total_rejected == 0:
            status = "SUCCESS"
            status_class = "success"
        else:
            status = "PARTIAL SUCCESS"
            status_class = "warning"
        
        html_content += f"""
            <div class="summary">
                <h2>Overall Status: <span class="{status_class}">{status}</span></h2>
                <p><strong>Total Records Processed:</strong> {total_read}</p>
                <p><strong>Successfully Loaded:</strong> {total_inserted + total_updated}</p>
                <p><strong>Rejected Records:</strong> {total_rejected}</p>
                <p><strong>New Records Added:</strong> {total_inserted}</p>
                <p><strong>Existing Records Updated:</strong> {total_updated}</p>
            </div>
        """
        
        # Table details
        html_content += """
            <h2>Table-by-Table Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Data Source</th>
                        <th>Target Table</th>
                        <th>Records Read</th>
                        <th>Successfully Loaded</th>
                        <th>Rejected</th>
                        <th>New Records</th>
                        <th>Updated Records</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Sort rows by sheet name for better readability (use already deduplicated rows)
        sorted_rows = sorted(unique_rows, key=lambda x: (x.get('sheet', ''), x.get('table', '')))
        
        for row in sorted_rows:
            if row.get('rejected_rows', 0) == 0 and row.get('read_rows', 0) > 0:
                status_text = "✓ SUCCESS"
                status_class = "success"
            elif row.get('rejected_rows', 0) > 0:
                status_text = "⚠ PARTIAL"
                status_class = "warning"
            elif row.get('read_rows', 0) == 0 and 'ERROR' in row.get('notes', ''):
                status_text = "✗ ERROR"
                status_class = "error"
            elif row.get('read_rows', 0) == 0 and row.get('inserted', 0) == 0 and row.get('updated', 0) == 0:
                # Skip empty rows (no activity) unless they have error notes
                continue
            else:
                status_text = "✗ ERROR"
                status_class = "error"
            
            # Add rejection details tooltip
            rejection_tooltip = ""
            if row.get('notes') and row.get('rejected_rows', 0) > 0:
                rejection_tooltip = f' title="{row.get("notes")}"'
            
            successfully_loaded = row.get('inserted', 0) + row.get('updated', 0)
            
            html_content += f"""
                    <tr>
                        <td>{row.get('sheet', 'N/A')}</td>
                        <td>{row.get('table', 'N/A')}</td>
                        <td>{row.get('read_rows', 0)}</td>
                        <td>{successfully_loaded}</td>
                        <td{rejection_tooltip}>{row.get('rejected_rows', 0)}</td>
                        <td>{row.get('inserted', 0)}</td>
                        <td>{row.get('updated', 0)}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        """
        
        # Add detailed rejection explanations section (use deduplicated rows)
        rejection_rows = [row for row in unique_rows if row.get('rejected_rows', 0) > 0]
        if rejection_rows:
            html_content += """
                <h2>Why Were Records Rejected?</h2>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <p><strong>For Business Users:</strong> The following explains exactly why records were rejected and what you need to do to fix them.</p>
                </div>
            """
            
            for row in rejection_rows:
                notes = row.get('notes', 'No details available')
                html_content += f"""
                    <div style="border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 15px; background-color: #f8f9fa;">
                        <h4>{row.get('sheet', 'Unknown Sheet')} → {row.get('table', 'Unknown Table')}</h4>
                        <p><strong>Rejected:</strong> {row.get('rejected_rows', 0)} out of {row.get('read_rows', 0)} records</p>
                        <p><strong>Reason:</strong> {notes}</p>
                        <div style="background-color: #e7f3ff; padding: 10px; border-radius: 3px; margin-top: 10px;">
                            <strong>📋 Action Required:</strong>
                            <ul style="margin: 5px 0;">
                """
                
                if "missing foreign key references" in notes:
                    html_content += """
                                <li>Add the missing materials to your material_master sheet</li>
                                <li>Ensure all material_ids in your data exist in the material_master sheet</li>
                    """
                    
                    # Add specific missing materials list if available
                    if self.missing_materials_data and self.missing_materials_data.get('missing_materials'):
                        missing_list = self.missing_materials_data['missing_materials']
                        total_missing = self.missing_materials_data.get('total_missing', len(missing_list))
                        
                        html_content += f"""
                            </ul>
                            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 3px; margin-top: 10px;">
                                <strong>Missing Material IDs ({total_missing} total):</strong>
                                <div style="max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; background-color: white; padding: 10px; border: 1px solid #ddd; margin-top: 5px;">
                        """
                        
                        # Show first 100 materials
                        display_count = min(100, len(missing_list))
                        for i, material_id in enumerate(missing_list[:display_count]):
                            html_content += f"{material_id}<br>"
                        
                        if total_missing > display_count:
                            html_content += f"<em>... and {total_missing - display_count} more materials</em>"
                        
                        html_content += """
                                </div>
                            </div>
                            <ul style="margin: 5px 0;">
                        """
                elif "Missing required data" in notes:
                    html_content += """
                                <li>Fill in the required fields that are currently empty</li>
                                <li>Check for missing primary keys or mandatory data</li>
                                <li>Review the rejected_*.csv file for specific row details</li>
                    """
                else:
                    html_content += f"""
                                <li>Review the technical details: {notes}</li>
                                <li>Check the rejected_*.csv file for specific row details</li>
                                <li>Contact your system administrator if you need help</li>
                    """
                
                html_content += """
                            </ul>
                        </div>
                    </div>
                """
        
        # Add business-friendly issues section
        if self.business_issues:
            html_content += """
                <h2>Action Items - What Needs to be Fixed</h2>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <p><strong>For Business Users:</strong> The following issues need your attention to complete the data load successfully.</p>
                </div>
            """
            
            for issue in self.business_issues:
                html_content += f"""
                    <div style="border-left: 4px solid #dc3545; padding: 15px; margin-bottom: 15px; background-color: #f8f9fa;">
                        <h4>{issue['sheet']} (Table: {issue['table']})</h4>
                        <p><strong>Issue:</strong> {issue['issue']}</p>
                        <p><strong>{issue['action_needed']}</strong></p>
                    </div>
                """
        
        # Add technical details section (collapsible)
        notes_rows = [row for row in self.rows if row.get('notes')]
        if notes_rows:
            html_content += """
                <details style="margin-top: 30px;">
                    <summary style="cursor: pointer; font-weight: bold; color: #6c757d;">Technical Details (Click to expand)</summary>
                    <div style="margin-top: 10px; background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                        <p><em>For technical staff and debugging purposes:</em></p>
                        <ul>
            """
            for row in notes_rows:
                html_content += f"<li><strong>{row.get('table', 'Unknown')}:</strong> {row.get('notes', '')}</li>"
            html_content += """
                        </ul>
                    </div>
                </details>
            """
        
        html_content += """
            <div style="margin-top: 30px; padding: 15px; background-color: #f9f9f9; border-radius: 5px;">
                <h3>What This Report Means:</h3>
                <ul>
                    <li><strong>Records Read:</strong> Total rows found in the Excel file</li>
                    <li><strong>Successfully Loaded:</strong> Rows that passed validation and were loaded into the database</li>
                    <li><strong>Rejected:</strong> Rows that had errors (missing data, wrong format, etc.) - check rejected CSV files for details</li>
                    <li><strong>New Records:</strong> Rows that were inserted for the first time</li>
                    <li><strong>Updated Records:</strong> Existing rows that were updated with new data</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Ensure directory exists before writing
        os.makedirs(os.path.dirname(self.summary_path), exist_ok=True)
        with open(self.summary_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


