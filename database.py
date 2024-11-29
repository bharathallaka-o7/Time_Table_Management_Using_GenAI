import pandas as pd
import sqlite3
from sqlalchemy import create_engine

def excel_to_sqlite(excel_file, db_file, table_name):
    # Read the Excel file
    df = pd.read_excel(excel_file)
    
    # Create a connection to the SQLite database
    engine = create_engine(f'sqlite:///{db_file}')
    
    # Write the dataframe to SQLite
    df.to_sql(table_name, engine, index=False, if_exists='replace')
    
    print(f"Data from {excel_file} has been written to {db_file} in table {table_name}")

# Example usage
excel_file = "CSE_faculty_formatted.xlsx"
db_file = 'faculty.db'
table_name = 'faculty'

excel_to_sqlite(excel_file, db_file, table_name)