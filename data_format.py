import pandas as pd

# Paths to the Excel files
file_ece = "Modified Data\ECE\ece.xlsx"
file_eee = "Modified Data\EEE\EEE1.xlsx"

# Load the Excel files
ece_data = pd.ExcelFile(file_ece)
eee_data = pd.ExcelFile(file_eee)

# Function to normalize and clean the data
def format_for_database(excel_file):
    formatted_data = {}
    for sheet in excel_file.sheet_names:
        df = excel_file.parse(sheet)
        
        # Ensure column names are consistent
        df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
        
        # Add unique ID column (if not already present)
        if "id" not in df.columns:
            df.insert(0, "id", range(1, len(df) + 1))
        
        # Remove empty rows and columns
        df = df.dropna(how="all")  # Drop rows where all values are NaN
        df = df.dropna(axis=1, how="all")  # Drop columns where all values are NaN
        
        # Normalize data types
        df = df.convert_dtypes()  # Automatically converts to appropriate data types
        
        # Store the cleaned sheet
        formatted_data[sheet] = df
    return formatted_data

# Process both files
ece_formatted = format_for_database(ece_data)
eee_formatted = format_for_database(eee_data)

# Save the formatted data to new Excel files
with pd.ExcelWriter("formatted_ece.xlsx") as writer:
    for sheet, df in ece_formatted.items():
        df.to_excel(writer, index=False, sheet_name=sheet)

with pd.ExcelWriter("formatted_eee.xlsx") as writer:
    for sheet, df in eee_formatted.items():
        df.to_excel(writer, index=False, sheet_name=sheet)

print("Files have been formatted and saved as 'formatted_ece.xlsx' and 'formatted_eee.xlsx'.")
