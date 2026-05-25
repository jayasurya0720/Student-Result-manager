import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, create_table

st.set_page_config(page_title="Student Result Manager", layout="wide", page_icon="🎓")

create_table()

st.title("🎓 Student Result Manager")
st.markdown("### Manage 100+ student academic records")

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Add Student", "View All Students", "Search & Update", "Performance Analytics"]
)

# ------------------- DASHBOARD -------------------
if menu == "Dashboard":
    st.header("📊 Dashboard")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Students", len(df))
        with col2: st.metric("Avg Percentage", f"{df['percentage'].mean():.2f}%" if not df.empty else "0%")
        with col3: st.metric("Top Grade", df['grade'].mode()[0] if not df.empty else "N/A")
        with col4: st.metric("Classes", df['class'].nunique() if not df.empty else 0)

# ------------------- ADD STUDENT -------------------
elif menu == "Add Student":
    st.header("➕ Add New Student")
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            roll_no = st.text_input("Roll Number *")
            name = st.text_input("Full Name *")
            class_name = st.selectbox("Class", [str(i) for i in range(1,13)])
            section = st.selectbox("Section", ["A", "B", "C", "D"])
        with col2:
            sub1 = st.number_input("Subject 1", 0, 100, 0)
            sub2 = st.number_input("Subject 2", 0, 100, 0)
            sub3 = st.number_input("Subject 3", 0, 100, 0)
            sub4 = st.number_input("Subject 4", 0, 100, 0)
            sub5 = st.number_input("Subject 5", 0, 100, 0)
        
        if st.form_submit_button("Add Student"):
            if roll_no and name:
                total = sub1 + sub2 + sub3 + sub4 + sub5
                percentage = total / 5.0
                if percentage >= 90: grade = "A+"
                elif percentage >= 80: grade = "A"
                elif percentage >= 70: grade = "B"
                elif percentage >= 60: grade = "C"
                else: grade = "D"
                
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO students 
                            (roll_no, name, class, section, subject1, subject2, subject3, subject4, subject5, total, percentage, grade)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (roll_no, name, class_name, section, sub1, sub2, sub3, sub4, sub5, total, percentage, grade))
                        conn.commit()
                        st.success("✅ Student added successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
            else:
                st.error("Roll Number and Name are required!")

# ------------------- VIEW ALL -------------------
elif menu == "View All Students":
    st.header("📋 All Students")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students ORDER BY percentage DESC", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No students added yet.")

# ------------------- SEARCH & UPDATE (Fixed) -------------------
elif menu == "Search & Update":
    st.header("🔍 Search & Update")
    
    search = st.text_input("Search by Roll No or Name")
    
    conn = get_connection()
    if conn:
        if search:
            df = pd.read_sql("""
                SELECT * FROM students 
                WHERE roll_no LIKE %s OR name LIKE %s
            """, conn, params=(f"%{search}%", f"%{search}%"))
        else:
            df = pd.read_sql("SELECT * FROM students", conn)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Update / Delete
        st.subheader("Update or Delete Record")
        roll_to_edit = st.text_input("Enter Roll Number to Edit/Delete")
        
        if roll_to_edit:
            student_df = pd.read_sql("SELECT * FROM students WHERE roll_no = %s", conn, params=(roll_to_edit,))
            if not student_df.empty:
                st.write("Current Record:", student_df)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑 Delete Record"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll_to_edit,))
                        conn.commit()
                        st.success("Record deleted!")
                        st.rerun()
                
                with col2:
                    if st.button("✏️ Update Later (Coming Soon)"):
                        st.info("Update feature will be added soon.")
            else:
                st.warning("No record found with this Roll Number.")
        conn.close()

# ------------------- PERFORMANCE ANALYTICS (Fixed) -------------------
elif menu == "Performance Analytics":
    st.header("📈 Performance Analytics")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        
        if not df.empty:
            tab1, tab2, tab3 = st.tabs(["Grade Distribution", "Class Performance", "Top Performers"])
            
            with tab1:
                fig = px.pie(df, names='grade', title="Grade Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = px.box(df, x='class', y='percentage', title="Performance by Class")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                top = df.nlargest(10, 'percentage')
                st.dataframe(top[['roll_no', 'name', 'class', 'percentage', 'grade']], hide_index=True)
        else:
            st.info("No data available. Add some students first!")

st.sidebar.info("Built with ❤️ using Streamlit + MySQL")