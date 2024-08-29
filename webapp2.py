import streamlit as st
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os
import google.generativeai as genai
import plotly.express as px

# Load environment variables
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro model
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text

# Function to generate SQL query using prompt and question
def generate_sql_query(prompt, question):
    full_prompt = f"{prompt}\n{question}"
    sql_query = get_gemini_response(full_prompt).strip()
    return sql_query

# Function to execute an SQL query on the database
def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

# Function to retrieve query results from the database 
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Function to add a column to the database
def add_column_to_db(db_path, column_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE TIMETABLE ADD COLUMN {column_name} TEXT")
    conn.commit()
    conn.close()

# Function to map Excel columns to database columns using Gemini Pro API
def map_columns(excel_columns, db_columns):
    mappings = {}
    for excel_col in excel_columns:
        prompt = f"Find the best match for the column '{excel_col}' from the following options: {', '.join(db_columns)}"
        best_match = get_gemini_response(prompt).strip()
        mappings[excel_col] = best_match
    return mappings

# Function to process the Excel file and update the database
def process_excel_file(uploaded_file, db_path, action):
    df = pd.read_excel(uploaded_file)
    st.write("Column names in the uploaded file:", df.columns.tolist())

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(TIMETABLE)")
    existing_columns = [info[1] for info in cursor.fetchall()]

    column_mappings = map_columns(df.columns, existing_columns)

    for excel_col, db_col in column_mappings.items():
        if db_col not in existing_columns:
            add_column_to_db(db_path, db_col)
            existing_columns.append(db_col)

    for index, row in df.iterrows():
        mapped_row = {column_mappings[col]: value for col, value in row.items()}

        if action == "remove":
            cursor.execute("DELETE FROM TIMETABLE WHERE NAME=?", (mapped_row.get('NAME'),))

        elif action == "modify":
            set_clause = ", ".join([f"{col}=?" for col in mapped_row.keys()])
            values = tuple(mapped_row.values())
            cursor.execute(f"UPDATE TIMETABLE SET {set_clause} WHERE NAME=?", values + (mapped_row.get('NAME'),))

        else:
            cursor.execute("SELECT * FROM TIMETABLE WHERE NAME=?", (mapped_row.get('NAME'),))
            existing_entry = cursor.fetchone()
            if existing_entry:
                set_clause = ", ".join([f"{col}=?" for col in mapped_row.keys()])
                values = tuple(mapped_row.values())
                cursor.execute(f"UPDATE TIMETABLE SET {set_clause} WHERE NAME=?", values + (mapped_row.get('NAME'),))
            else:
                columns = ", ".join(mapped_row.keys())
                placeholders = ", ".join(["?" for _ in mapped_row])
                values = tuple(mapped_row.values())
                cursor.execute(f"INSERT INTO TIMETABLE ({columns}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()

# Defining your prompts
sql_prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name TIMETABLE and has the following columns: CLASS, DAY, TIME, SUBJECT, PROFESSOR, ROOM.
For example:
Example 1: What is the timetable for Monday?
The SQL command will be something like this: SELECT * FROM TIMETABLE WHERE DAY='Monday';
Example 2: Who is teaching Mathematics on Wednesday?
The SQL command will be something like this: SELECT PROFESSOR FROM TIMETABLE WHERE SUBJECT='Mathematics' AND DAY='Wednesday';
The SQL code should not have ' in the beginning or end and 'sql' word in output.
"""

modification_prompt = """
You are an expert in converting English commands to SQL queries for database modification!
The SQL database has the name TIMETABLE and has the following columns: CLASS, DAY, TIME, SUBJECT, PROFESSOR, ROOM.
For example:
Example 1: Add a new class on Monday at 10 AM for Mathematics taught by Prof. John in Room 101.
The SQL command will be something like this: INSERT INTO TIMETABLE (CLASS, DAY, TIME, SUBJECT, PROFESSOR, ROOM) VALUES ('CLASS1', 'Monday', '10:00 AM', 'Mathematics', 'Prof. John', 'Room 101');
Example 2: Remove the class on Monday at 10 AM.
The SQL command will be something like this: DELETE FROM TIMETABLE WHERE DAY='Monday' AND TIME='10:00 AM';
Example 3: Update the room for the Mathematics class on Monday at 10 AM to Room 102.
The SQL command will be something like this: UPDATE TIMETABLE SET ROOM='Room 102' WHERE SUBJECT='Mathematics' AND DAY='Monday' AND TIME='10:00 AM';
The SQL code should not have ' in the beginning or end and 'sql' word in output.
"""

# Streamlit Page Configuration
st.set_page_config(
    page_title="Timetable Management Using GenAI",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    body {
        color: #fff;
        background-color: #0e1117;
    }
    .main {
        background-color: #1a1b21;
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        color: #1DB954;
        text-align: center;
        font-size: 2.5em;
    }
    .input-section, .dashboard-section, .modification-section, .upload-section {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-section {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
    }
    .error {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
        color: #d32f2f;
    }
    .stTextInput>div>div>input {
        background-color: #3c404a;
        color: #fff;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #1DB954;
        color: #fff;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1ed760;
        color: #fff;
    }
    .metric-card {
        background-color: #3c404a;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #1DB954;
    }
    .metric-label {
        font-size: 0.9em;
        color: #a0a0a0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Menu")
st.sidebar.markdown("Navigate through the options:")
page = st.sidebar.selectbox("Choose a page", ["Ask Question About the Timetable", "Timetable Dashboard", "Modify Timetable"])

if page == "Ask Question About the Timetable":
    # Streamlit App for Text to SQL
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Ask any question about Timetable</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    question = st.text_input("Enter your question about the timetable:")
    if st.button("Submit"):
        if question:
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.write("Generating SQL query...")
            sql_query = generate_sql_query(sql_prompt, question)
            st.write(f"Generated SQL query: {sql_query}")

            st.write("Fetching data from the database...")
            db_path = '/home/mukesh/Github-my repos/Mini projet/Time_Table_Management_Using_GenAI/timetable.db'
            try:
                results = read_sql_query(sql_query, db_path)
                if not results.empty:
                    st.write("Query Results:")
                    st.dataframe(results)
                else:
                    st.write("No results found.")
            except Exception as e:
                st.markdown('<div class="error">', unsafe_allow_html=True)
                st.write(f"Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Timetable Dashboard":
    # Streamlit App for Dashboard
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Timetable Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)

    db_path = 'timetable.db'
    df = read_sql_query("SELECT * FROM TIMETABLE", db_path)

    st.write("### Timetable Overview")
    st.dataframe(df)

    st.write("### Class Distribution by Day")
    fig = px.histogram(df, x='DAY', title='Class Distribution by Day')
    st.plotly_chart(fig)

    st.write("### Class Distribution by Subject")
    fig = px.histogram(df, x='SUBJECT', title='Class Distribution by Subject')
    st.plotly_chart(fig)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Modify Timetable":
    # Streamlit App for Modifying Timetable
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Modify Timetable</div>', unsafe_allow_html=True)
    st.markdown('<div class="modification-section">', unsafe_allow_html=True)
    
    action = st.radio("Choose an action", ["add", "modify", "remove"])
    modification_command = st.text_input("Enter your modification command:")
    
    if st.button("Submit Modification"):
        if modification_command:
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.write("Generating SQL query...")
            sql_query = generate_sql_query(modification_prompt, modification_command)
            st.write(f"Generated SQL query: {sql_query}")

            st.write("Executing query on the database...")
            db_path = 'timetable.db'
            try:
                execute_sql_query(sql_query, db_path)
                st.write("Modification successful.")
            except Exception as e:
                st.markdown('<div class="error">', unsafe_allow_html=True)
                st.write(f"Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload an Excel file to modify the timetable:", type=["xlsx"])
    action = st.selectbox("Select an action for the uploaded data:", ["add", "modify", "remove"])
    
    if uploaded_file and st.button("Process File"):
        st.write("Processing file...")
        try:
            process_excel_file(uploaded_file, 'timetable.db', action)
            st.write("File processed successfully.")
        except Exception as e:
            st.markdown('<div class="error">', unsafe_allow_html=True)
            st.write(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)