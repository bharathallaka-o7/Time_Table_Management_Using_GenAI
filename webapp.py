import streamlit as st
import pandas as pd
import sqlite3

# Function to retrieve timetable based on class and day selection
def get_timetable(block, year, section, day):
    db_path = 'timetable.db'
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT ROOM, STRENGTH, {day.upper()}_P1 AS P1, {day.upper()}_P2 AS P2, {day.upper()}_P3 AS P3, 
           {day.upper()}_P4 AS P4, {day.upper()}_P5 AS P5, {day.upper()}_P6 AS P6, {day.upper()}_P7 AS P7
    FROM TIMETABLE
    WHERE BLOCK='{block}' AND YEAR='{year}' AND SECTION='{section}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit Page Configuration
st.set_page_config(
    page_title="CSE Timetable Viewer",
    page_icon=":calendar:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit App UI
st.title("CSE Timetable Viewer")

# Input Section
st.sidebar.title("Select Class and Day")

# Dropdowns for class selection
block = st.sidebar.selectbox("Block", ["AB-02"])
year = st.sidebar.selectbox("Year", ["E1"])
section = st.sidebar.selectbox("Section", ["CSE-01", "CSE-02", "CSE-03", "CSE-04", "CSE-05", "CSE-06"])

# Dropdown for day selection
day = st.sidebar.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

# Display timetable based on selections
if st.sidebar.button("Get Timetable"):
    timetable_df = get_timetable(block, year, section, day)
    
    if not timetable_df.empty:
        st.write(f"### Timetable for {block}, {year}, {section} on {day}")
        st.dataframe(timetable_df)
    else:
        st.write("No timetable data found for the selected options.")
