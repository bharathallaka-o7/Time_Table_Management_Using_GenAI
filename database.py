import os
import pandas as pd
from sqlalchemy import create_engine

# Directory structure
MODIFIED_DATA_DIR = "Modified Data"
DATABASE_DIR = "Database"

BRANCH_CONFIG = {
    "CSE": {
        "excel_files": {
            "timetable": "CSE_only_periods.xlsx",
            "faculty": "CSE_faculty_formatted.xlsx",
            "timings": "period_schedule.xlsx",
        },
        "databases": {
            "timetable_db": "cse_timetable.db",
            "faculty_db": "cse_faculty.db",
            "timings_db": "cse_timings.db",
        },
    },
    "ECE": {
        "excel_files": {
            "timetable": "ECE_Timetable.xlsx",
            "faculty": "formatted_ece.xlsx",
            "timings": "period_schedule.xlsx",
        },
        "databases": {
            "timetable_db": "ece_timetable.db",
            "faculty_db": "ece_faculty.db",
            "timings_db": "ece_timings.db",
        },
    },
    "MECH": {
        "excel_files": {
            "timetable":"MechtimeTable.xlsx" ,
            "faculty": "MECH.xlsx",  # Faculty data not provided
            "timings": "period_schedule.xlsx",
        },
        "databases": {
            "timetable_db": "mech_timetable.db",
            "faculty_db": "mech_faculty.db",  # No faculty database
            "timings_db": "mech_timings.db",
        },
    },
    "EEE": {
        "excel_files": {
            "timetable": "EEE_only_periods.xlsx",
            "faculty": "formatted_eee.xlsx",
            "timings": "period_schedule.xlsx",
        },
        "databases": {
            "timetable_db": "eee_timetable.db",
            "faculty_db": "eee_faculty.db",
            "timings_db": "eee_timings.db",
        },
    },
    "CHEM": {
        "excel_files": {
            "timetable": "CHEMTimeTable.xlsx",
            "faculty": None,  # No faculty data for CHEM
            "timings": "period_schedule.xlsx",
        },
        "databases": {
            "timetable_db": "chem_timetable.db",
            "faculty_db": None,  # No faculty database
            "timings_db": "chem_timings.db",
        },
    },
}

def excel_to_sqlite(excel_file, db_file, table_name):
    """Convert an Excel file to an SQLite database."""
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return

    # Read the Excel file
    df = pd.read_excel(excel_file)

    # Create a connection to the SQLite database
    engine = create_engine(f'sqlite:///{db_file}')

    # Write the DataFrame to the SQLite database
    df.to_sql(table_name, engine, index=False, if_exists='replace')

    print(f"Data from {excel_file} has been written to {db_file} in table {table_name}")

def process_branch(branch, config):
    """Process a branch by converting its Excel files into SQLite databases."""
    excel_dir = os.path.join(MODIFIED_DATA_DIR, branch)
    db_dir = os.path.join(DATABASE_DIR, branch)

    # Create the branch database directory if it doesn't exist
    os.makedirs(db_dir, exist_ok=True)

    for db_key, db_file in config["databases"].items():
        if db_file is None:
            continue  # Skip if no database is specified

        table_name = db_key.split("_")[0]  # e.g., 'timetable' from 'timetable_db'
        excel_file = config["excel_files"].get(table_name)

        if excel_file:
            excel_path = os.path.join(excel_dir, excel_file)
            db_path = os.path.join(db_dir, db_file)
            excel_to_sqlite(excel_path, db_path, table_name)

# Process each branch
for branch, config in BRANCH_CONFIG.items():
    process_branch(branch, config)

print("All branches processed successfully!")
