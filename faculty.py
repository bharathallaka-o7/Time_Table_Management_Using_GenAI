import streamlit as st
import pandas as pd
import sqlite3

# Database configuration
db_file = 'faculty.db'  # SQLite database file
table_name = 'faculty'  # Table name in the database

# Function to retrieve unique years from the database
def get_years(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT YEAR FROM {table_name}")
        years = cursor.fetchall()
        # Filter out None values and convert to a list of strings
        years = [str(row[0]) for row in years if row[0] is not None]
        return sorted(set(years))  # Return sorted, unique years
    except Exception as e:
        st.error(f"Error retrieving years: {e}")
        return []

# Function to retrieve unique sections from the database
def get_sections(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT sections FROM {table_name}")
        sections = cursor.fetchall()
        # Filter out None values, convert to strings, and clean up
        sections = [str(row[0]).strip() for row in sections if row[0] is not None]
        # Handle multiple sections within a single record
        all_sections = []
        for section in sections:
            split_sections = section.replace(' ', '').split(',')
            for s in split_sections:
                if s and s not in all_sections:  # Avoid duplicates
                    all_sections.append(s)
        return sorted(set(all_sections))  # Return sorted, unique sections
    except Exception as e:
        st.error(f"Error retrieving sections: {e}")
        return []

# Function to retrieve unique subjects from the database
def get_subjects(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT Subject FROM {table_name}")
        subjects = cursor.fetchall()
        # Filter out None values and convert to a list of strings
        subjects = [str(row[0]) for row in subjects if row[0] is not None]
        return sorted(set(subjects))  # Return sorted, unique subjects
    except Exception as e:
        st.error(f"Error retrieving subjects: {e}")
        return []

# Function to retrieve timetable based on selected criteria
def get_timetable(conn, year=None, section=None, subject=None):
    # Base query to fetch timetable data
    query = f"SELECT YEAR, subject_code, Subject, Name, sections FROM {table_name} WHERE 1=1"
    params = []

    # Add conditions to the query based on user inputs
    if year:
        query += " AND YEAR = ?"
        params.append(year)
    if section:
        # Handle variations in section formats with LIKE
        query += " AND (sections LIKE ? OR sections LIKE ?)"
        params.append(f"%{section}%")
        params.append(f"%{section} %")
    if subject:
        query += " AND Subject = ?"
        params.append(subject)

    # Execute the query and return results as a DataFrame
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error retrieving timetable: {e}")
        return pd.DataFrame()

# Streamlit page configuration
st.set_page_config(
    page_title="CSE Timetable Viewer",  # Page title
    page_icon=":calendar:",  # Icon for the page
    layout="wide",  # Layout: wide mode
    initial_sidebar_state="expanded",  # Sidebar state
)

# Main app function
def main():
    st.title("CSE Timetable Viewer")  # Main app title

    # Establish database connection
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return

    # Sidebar for filtering options
    st.sidebar.title("Filter Timetable")

    # Retrieve filter options from the database
    years = get_years(conn)
    sections = get_sections(conn)
    subjects = get_subjects(conn)

    # Check if data was retrieved successfully
    if not years or not sections or not subjects:
        st.error("Unable to retrieve data from the database. Please check the database connection and table contents.")
        conn.close()
        return

    # Sidebar dropdowns for filtering criteria
    year = st.sidebar.selectbox("Select Year", ["All"] + years)
    section = st.sidebar.selectbox("Select Section", ["All"] + sections)
    subject = st.sidebar.selectbox("Select Subject", ["All"] + subjects)

    # Convert "All" to None for query parameters
    year = None if year == "All" else year
    section = None if section == "All" else section
    subject = None if subject == "All" else subject

    # Button to fetch timetable data
    if st.sidebar.button("Get Timetable"):
        try:
            # Retrieve filtered timetable data
            timetable_df = get_timetable(conn, year, section, subject)

            if not timetable_df.empty:
                # Display selected filters
                filter_criteria = []
                if year: filter_criteria.append(f"Year: {year}")
                if section: filter_criteria.append(f"Section: {section}")
                if subject: filter_criteria.append(f"Subject: {subject}")

                # Display timetable data
                st.write(f"### Timetable Results")
                if filter_criteria:
                    st.write(f"*Filters:* {', '.join(filter_criteria)}")
                st.dataframe(timetable_df[['YEAR', 'subject_code', 'Subject', 'Name', 'sections']])

                # Show additional stats
                st.write(f"**Total Records:** {len(timetable_df)}")
            else:
                st.warning("No timetable data found for the selected criteria.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Close database connection
    conn.close()

# Run the app
if __name__ == "__main__":
    main()
