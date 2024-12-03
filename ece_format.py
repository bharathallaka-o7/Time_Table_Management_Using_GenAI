import pandas as pd

def uppercase_first_column(filepath):
    """
    Reads a Excel file, converts the first column to uppercase, and saves the modified file.

    Args:
        filepath: Path to the Excel file.
    """
    try:
        df = pd.read_excel(filepath)  # Read the CSV file into a pandas DataFrame

        #Check if the DataFrame is empty
        if df.empty:
            print("Error: The CSV file is empty.")
            return

        #Check if the DataFrame has at least one column
        if len(df.columns) == 0:
            print("Error: The CSV file has no columns.")
            return

        df.iloc[:, 0] = df.iloc[:, 0].str.upper() # Convert the first column to uppercase
        filepath_1=f'{filepath}'
        df.to_excel(filepath_1, index=False) #Save the modified DataFrame back to the CSV file

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file at {filepath} is empty.")
    except pd.errors.ParserError:
        print(f"Error: Could not parse the CSV file at {filepath}. Please check the file format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Example usage
filepath = "Modified Data/ECE/ECE_Timetable.xlsx"  # Replace with your file path
uppercase_first_column(filepath)
