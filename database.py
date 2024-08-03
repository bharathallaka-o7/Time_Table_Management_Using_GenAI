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
excel_file = 'csetimetable.xlsx'
db_file = 'time_table.db'
table_name = 'time_table'

excel_to_sqlite(excel_file, db_file, table_name)