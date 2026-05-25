import mysql.connector
import streamlit as st

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

def create_table():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                roll_no VARCHAR(20) UNIQUE,
                name VARCHAR(100),
                class VARCHAR(20),
                section VARCHAR(5),
                subject1 INT,
                subject2 INT,
                subject3 INT,
                subject4 INT,
                subject5 INT,
                total INT,
                percentage FLOAT,
                grade VARCHAR(5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()