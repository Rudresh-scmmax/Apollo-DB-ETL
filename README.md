# Excel Data Processing Script

This Python script processes the "Data Model + Tables + Data.xlsx" file according to the following requirements:

## Features

1. **Column Name Cleaning**: 
   - Removes leading and trailing spaces
   - Replaces spaces with underscores
   - Converts all column names to lowercase

2. **Hyperlink Creation**:
   - Creates links between Summary and Sequence tabs and their respective table tabs
   - Hyperlinks are styled in blue with underlines

## Requirements

Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure the "Data Model + Tables + Data.xlsx" file is in the same directory as the script
2. Run the script:
```bash
python process_excel.py
```

## Output

The script will create a new file named "Data Model + Tables + Data_processed.xlsx" with:
- Cleaned column names (no spaces, lowercase)
- Hyperlinks between Summary/Sequence tabs and table tabs
- All original data preserved

## What the Script Does

1. **Reads all tabs** from the Excel file
2. **Processes column names** in each tab:
   - Strips whitespace
   - Replaces spaces with underscores
   - Converts to lowercase
3. **Creates hyperlinks** by:
   - Identifying Summary and Sequence tabs
   - Finding table names in these tabs
   - Creating clickable links to the corresponding table tabs
4. **Saves the processed file** with all changes

## Error Handling

The script includes comprehensive error handling and will display:
- Progress information for each step
- Column name mappings (showing before/after)
- Any errors that occur during processing 