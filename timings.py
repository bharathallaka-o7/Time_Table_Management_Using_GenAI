import streamlit as st
import pandas as pd
import sqlite3

# Database configuration
db_file = 'timings.db'  # SQLite database file
table_name = 'timings'  # Table name in the database

# Function to retrieve unique periods from the database
def get_periods(conn):
    """
    Retrieves a list of unique periods from the database.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT Period FROM {table_name}")
        periods = cursor.fetchall()
        periods = [str(row[0]) for row in periods if row[0] is not None]  # Convert to string and filter None
        return sorted(set(periods))  # Return sorted, unique periods
    except Exception as e:
        st.error(f"Error retrieving periods: {e}")
        return []

# Function to retrieve timetable based on selected period
def get_timetable(conn, period=None):
    """
    Retrieves timetable data filtered by period.
    """
    query = f"SELECT Period,Start_Time,End_Time FROM {table_name} WHERE 1=1"
    params = []

    # Add condition for period
    if period:
        query += " AND Period = ?"
        params.append(period)

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
    page_icon=":calendar:",  # Page icon
    layout="wide",  # Use wide layout
    initial_sidebar_state="expanded",  # Expand sidebar by default
)

# Main app function
def main():
    st.title("CSE Timetable Viewer")  # App title

    # Connect to SQLite database
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return

    # Sidebar for filter options
    st.sidebar.title("Filter Timetable")

    # Branch dropdown (only "CSE" as an option)
    branch = st.sidebar.selectbox("Select Branch", ["CSE"])  # Branch filter (static)

    # Retrieve periods from the database
    periods = get_periods(conn)

    # Check if periods were successfully retrieved
    if not periods:
        st.error("Unable to retrieve data from the database. Please check the database connection and table contents.")
        conn.close()
        return

    # Sidebar dropdown menu for periods
    period = st.sidebar.selectbox("Select Period", ["All"] + periods)  # Period filter

    # Convert "All" to None for query filtering
    period = None if period == "All" else period

    # Fetch and display timetable when the button is clicked
    if st.sidebar.button("Get Timetable"):
        try:
            timetable_df = get_timetable(conn, period)  # Retrieve timetable

            if not timetable_df.empty:
                # Display filters applied
                filter_criteria = []
                filter_criteria.append(f"Branch: {branch}")
                if period: filter_criteria.append(f"Period: {period}")

                st.write(f"### Timetable Results")  # Timetable title
                if filter_criteria:
                    st.write(f"*Filters:* {', '.join(filter_criteria)}")

                # Display timetable DataFrame
                st.dataframe(timetable_df)

                # Show total record count
                st.write(f"**Total Records:** {len(timetable_df)}")
            else:
                st.warning("No timetable data found for the selected criteria.")  # No results warning
        except Exception as e:
            st.error(f"An error occurred: {e}")  # Error message

    # Close database connection
    conn.close()

# Run the app
if __name__ == "__main__":
    main()
