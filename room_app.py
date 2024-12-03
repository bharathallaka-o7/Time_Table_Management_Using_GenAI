import os
import streamlit as st
import pandas as pd
import sqlite3

# Base directory for databases
BASE_DIR = os.path.join(os.getcwd(), "Database")

# Branch configurations with room details
BRANCH_CONFIG = {
    
    "ECE": {
        "rooms": [
            "AB-2-SS1", "AB-2-SS2", "AB-2-SS3", "AB-2-SS4", "AB-2-SS5", "AB-2-SS6", "AB-2-SS7", "AB-2-SS8",
            "AB-2-SS9", "AB-2-SS10", "AB-2-G1", "AB-2-G2", "AB-2-G3", "AB-2-G4", "AB-2-G5", "AB-2-G6",
            "AB-2-T1", "AB-2-T2"
        ],
        "timetable_db": os.path.join(BASE_DIR, "ECE", "ece_timetable.db"),
        "faculty_db": os.path.join(BASE_DIR, "ECE", "ece_faculty.db"),
        "timings_db": os.path.join(BASE_DIR, "ECE", "ece_timings.db"),
    },
    "EEE": {
        "rooms": ["AB-2-T10", "AB-2-T7", "AB-2-T5", "AB-2-T6", "AB-2-T1", "AB-2-T2","AB-2-T9"],
        "timetable_db": os.path.join(BASE_DIR, "EEE", "eee_timetable.db"),
        "faculty_db": os.path.join(BASE_DIR, "EEE", "eee_faculty.db"),
        "timings_db": os.path.join(BASE_DIR, "EEE", "eee_timings.db"),
    },
    "MECH": {
        "rooms": ["AB-3-F2", "AB-3-F4", "AB-3-F5", "AB-3-F6"],
        "timetable_db": os.path.join(BASE_DIR, "MECH", "mech_timetable.db"),
        "faculty_db": os.path.join(BASE_DIR, "MECH", "mech_faculty.db"),
        "timings_db": os.path.join(BASE_DIR, "MECH", "mech_timings.db"),
    },
}

# Helper function to get branch by room
def get_branch_by_room(room):
    for branch, config in BRANCH_CONFIG.items():
        if room in config["rooms"]:
            return branch
    return None

# Function to retrieve timetable data with section information
def get_timetable_data(branch, block, room, day, periods):
    db_path = BRANCH_CONFIG[branch]["timetable_db"]
    conn = sqlite3.connect(db_path)

    # Construct the dynamic column names for the specific day and periods
    selected_periods = [f"{day.upper()}_{period}" for period in periods]
    selected_columns = ', '.join(selected_periods)

    query = f"""
        SELECT BLOCK, YEAR, SECTION, ROOM, STRENGTH, {selected_columns}
        FROM TIMETABLE
        WHERE BLOCK = ? AND ROOM = ?
    """
    params = (block, room)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Function to retrieve faculty details with section filtering
def get_faculty_details(branch, subjects, year='', section=''):
    faculty_db = BRANCH_CONFIG[branch]["faculty_db"]
    conn = sqlite3.connect(faculty_db)
    placeholders = ",".join(["?"] * len(subjects))

    query = f"""
        SELECT Subject, Name AS Faculty_Name
        FROM faculty
        WHERE Subject IN ({placeholders})
    """

    # If year and section are provided, add them to the query
    if year and section:
        query += " AND Year = ? AND sections = ?"
        params = subjects + [year, section]
    else:
        params = subjects

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Function to retrieve period timings
def get_period_timings(branch, periods):
    db_path = BRANCH_CONFIG[branch]["timings_db"]
    conn = sqlite3.connect(db_path)
    placeholders = ",".join(["?"] * len(periods))
    query = f"SELECT Period, Start_Time, End_Time FROM timings WHERE Period IN ({placeholders})"
    df = pd.read_sql_query(query, conn, params=periods)
    conn.close()
    return df

# Function to export results to CSV
def export_to_csv(dataframe, filename="timetable_results.csv"):
    return dataframe.to_csv(index=False).encode('utf-8')

# Streamlit app configuration
st.set_page_config(
    page_title="Room Timetable Viewer",
    page_icon=":calendar:",
    layout="wide",
)

st.title("Integrated Timetable Viewer")

# Sidebar inputs
st.sidebar.title("Select Input Options")
block = st.sidebar.selectbox("Select Block", ["AB-02", "AB-03"])

# Get all rooms across branches for selected block
all_rooms = [
    room for branch, config in BRANCH_CONFIG.items() for room in config["rooms"] if room.startswith(block.replace("0", ""))
]
if not all_rooms:
    st.sidebar.warning("No rooms available for the selected block.")
else:
    room = st.sidebar.selectbox("Select Room", all_rooms)

    # Day and period selection
    day = st.sidebar.selectbox("Select Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    periods = st.sidebar.multiselect("Select Period(s)", ["P1", "P2", "P3", "P4", "P5", "P6", "P7"])

    # Button to fetch results
    if st.sidebar.button("Get Timetable"):
        if not room or not periods or not day:
            st.warning("Please select all options.")
        else:
            # Determine the branch by room
            branch = get_branch_by_room(room)
            if not branch:
                st.error("Room does not belong to a valid branch.")
            else:
                # Fetch timetable
                timetable_df = get_timetable_data(branch, block, room, day, periods)

                if timetable_df.empty:
                    st.warning("No data found for the selected inputs.")
                else:
                    st.write(f"### Timetable for Room: {room} on {day}")
                    
                    # Extract year and section
                    year = timetable_df['YEAR'].iloc[0]
                    section = timetable_df['SECTION'].iloc[0]

                    # Flatten periods into a list of subjects
                    selected_periods = [f"{day.upper()}_{period}" for period in periods]
                    subject_list = timetable_df[selected_periods].values.flatten()
                    subject_list = [sub for sub in subject_list if pd.notna(sub)]

                    # Get faculty details
                    faculty_df = get_faculty_details(branch, subject_list, year, section)

                    # Get timings
                    timings_df = get_period_timings(branch, periods)

                    # Merge results
                    final_df = pd.DataFrame({
                        "Period": periods,
                        "Subject": subject_list
                    }).merge(faculty_df, how="left", left_on="Subject", right_on="Subject")
                    
                    final_df = final_df.merge(timings_df, how="left", left_on="Period", right_on="Period")

                    # Add Room and Section columns
                    final_df["Room"] = room
                    final_df["Section"] = section

                    # Display results
                    st.dataframe(final_df)

                    # CSV download button
                    csv = export_to_csv(final_df)
                    st.download_button(
                        label="Download Timetable as CSV",
                        data=csv,
                        file_name="room_timetable_results.csv",
                        mime="text/csv",
                    )
