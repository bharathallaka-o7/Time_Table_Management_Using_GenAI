import streamlit as st
import pandas as pd
import sqlite3

# Database paths
timetable_db = "timetable.db"
faculty_db = "faculty.db"
timings_db = "timings.db"

# Function to retrieve timetable data
def get_timetable_data(block, year, section, day):
    conn = sqlite3.connect(timetable_db)
    query = f"""
        SELECT ROOM, STRENGTH, {day.upper()}_P1 AS P1, {day.upper()}_P2 AS P2, 
               {day.upper()}_P3 AS P3, {day.upper()}_P4 AS P4, 
               {day.upper()}_P5 AS P5, {day.upper()}_P6 AS P6, {day.upper()}_P7 AS P7
        FROM TIMETABLE
        WHERE BLOCK = ? AND YEAR = ? AND SECTION = ?
    """
    params = (block, year, section)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Function to retrieve faculty details for subjects along with year, section, and subject
def get_faculty_details(subjects, year, section):
    conn = sqlite3.connect(faculty_db)
    placeholders = ",".join(["?"] * len(subjects))
    query = f"""
        SELECT Year, Section, Subject, Name AS Faculty_Name
        FROM faculty
        WHERE Subject IN ({placeholders}) AND Year = ? AND Section = ?
    """
    params = subjects + [year, section]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Function to retrieve period timings
def get_period_timings():
    conn = sqlite3.connect(timings_db)
    query = "SELECT Period, Start_Time, End_Time FROM timings"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to export results to CSV
def export_to_csv(dataframe, filename="timetable_results.csv"):
    return dataframe.to_csv(index=False).encode('utf-8')

# Streamlit app configuration
st.set_page_config(
    page_title="Integrated Timetable Viewer",
    page_icon=":calendar:",
    layout="wide",
)

st.title("Integrated Timetable Viewer")

# Sidebar for input
st.sidebar.title("Filter Options")
block = st.sidebar.selectbox("Select Block", ["AB-1", "AB-2"])
branch = st.sidebar.selectbox("Select Branch", ["CSE"])
year = st.sidebar.selectbox("Select Year", ["E1", "E2", "E3", "E4"])
section = st.sidebar.selectbox("Select Section", ["CSE-01", "CSE-02", "CSE-03", "CSE-04", "CSE-05", "CSE-06"])
day = st.sidebar.selectbox("Select Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

# Button to fetch results
if st.sidebar.button("Get Timetable"):
    # Retrieve timetable data
    timetable_df = get_timetable_data(block, year, section, day)
    
    if timetable_df.empty:
        st.warning("No timetable data found for the selected options.")
    else:
        st.write(f"### Timetable for {block}, {year}, {section} on {day}")
        # Flatten periods into a list of subjects
        periods = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
        subject_list = timetable_df[periods].values.flatten()
        subject_list = [sub for sub in subject_list if pd.notna(sub)]

        # Get faculty details
        faculty_df = get_faculty_details(subject_list, year, section)

        # Get timings
        timings_df = get_period_timings()

        # Merge results
        final_df = pd.DataFrame({
            "Period": periods,
            "Subject": subject_list
        }).merge(faculty_df, how="left", left_on="Subject", right_on="Subject")
        
        final_df = final_df.merge(timings_df, how="left", left_on="Period", right_on="Period")

        # Display results
        st.dataframe(final_df)

        # CSV download button
        csv = export_to_csv(final_df)
        st.download_button(
            label="Download Timetable as CSV",
            data=csv,
            file_name="timetable_results.csv",
            mime="text/csv",
        )
