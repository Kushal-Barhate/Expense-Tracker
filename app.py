import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# Set page config - Must be the very first Streamlit command in the script
st.set_page_config(page_title="Financial Dashboard", layout="wide")

# Custom CSS to improve the app's appearance
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
local_css("style.css")

# Load user details for authentication
def authenticate_user(username, password):
    user_df = pd.read_csv('E:/c desktop/WealthWhiz-main/WealthWhiz-main/user_details.csv')
    user = user_df[(user_df['Login'] == username) & (user_df['Password'] == password)]
    return not user.empty

# Login form function
def login():
    st.markdown("<h1 style='color: #2c3e50;text-align: center;'>Expense Tracker Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center;'>Enter your credentials to access the dashboard.</p>", unsafe_allow_html=True)
        with st.form(key="login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
        
        if login_button:
            if username and password:
                # Authenticate using the CSV file
                if authenticate_user(username, password):
                    st.success("Login successful!")
                    st.session_state["logged_in"] = True
                    st.session_state["current_page"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")

def view_expenses():
    if os.path.exists("exp.csv"):
        # Load the expense data
        df = pd.read_csv("exp.csv")
        
        st.markdown("<h2 style='text-align: center;'>Expense Table</h2>", unsafe_allow_html=True)
        st.table(df)  # Display the DataFrame as a table

        # Allow the user to select a row to edit or delete
        st.markdown("<h3 style='text-align: center;'>Edit or Delete Expense</h3>", unsafe_allow_html=True)
        row_to_edit_or_delete = st.number_input("Select Row Number to Edit or Delete", min_value=0, max_value=len(df) - 1, step=1)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Selected Row"):
                st.session_state["row_to_edit"] = row_to_edit_or_delete
                st.session_state["edit_mode"] = True
        with col2:
            if st.button("Delete Selected Row"):
                # Delete the selected row
                df = df.drop(row_to_edit_or_delete).reset_index(drop=True)
                df.to_csv("exp.csv", index=False)
                st.success(f"Row {row_to_edit_or_delete} deleted successfully!")
                st.rerun()  # Refresh the page to reflect the changes

        # Edit form (if in edit mode)
        if "edit_mode" in st.session_state and st.session_state["edit_mode"]:
            with st.form(key="edit_expense_form"):
                st.write("Edit the selected expense:")
                amount = st.number_input("Amount", value=df.loc[row_to_edit_or_delete, "Amount"], min_value=0.01, step=0.01)
                category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"], index=["Food", "Transport", "Entertainment", "Bills", "Other"].index(df.loc[row_to_edit_or_delete, "Category"]))
                date = st.date_input("Date", value=datetime.strptime(df.loc[row_to_edit_or_delete, "Date"], '%Y-%m-%d'))
                time = st.text_input("Time", value=df.loc[row_to_edit_or_delete, "Time"])

                save_button = st.form_submit_button("Save Changes")
                cancel_button = st.form_submit_button("Cancel")

                if save_button:
                    # Update the DataFrame with the edited values
                    df.loc[row_to_edit_or_delete, "Amount"] = amount
                    df.loc[row_to_edit_or_delete, "Category"] = category
                    df.loc[row_to_edit_or_delete, "Date"] = date.strftime('%Y-%m-%d')
                    df.loc[row_to_edit_or_delete, "Time"] = time

                    # Save the updated DataFrame to the CSV file
                    df.to_csv("exp.csv", index=False)
                    st.success("Expense updated successfully!")
                    del st.session_state["edit_mode"]  # Exit edit mode
                    st.rerun()

                if cancel_button:
                    del st.session_state["edit_mode"]  # Exit edit mode
                    st.rerun()

    else:
        st.warning("No expenses found. Add some expenses to view them here.")

    # Add a button to go back to the dashboard
    if st.button("Back to Dashboard"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()

        
# Function to add an expense and save it to CSV
def add_expense():
    st.markdown("<h2 style='text-align: center;'>Add Expense</h2>", unsafe_allow_html=True)

    with st.form(key="expense_form"):
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
        date = st.date_input("Date", value=datetime.today())
        submit_button = st.form_submit_button("Add Expense")

    if submit_button:
        if amount > 0 and category and date:
            # Capture current time when expense is added
            current_time = datetime.now().strftime('%H:%M:%S')

            # Prepare the new expense entry with time
            new_expense = pd.DataFrame({
                "Amount": [amount],
                "Category": [category],
                "Date": [date.strftime('%Y-%m-%d')],
                "Time": [current_time]
            })

            # Check if CSV file exists
            if os.path.exists("exp.csv"):
                # Load existing data
                df = pd.read_csv("exp.csv")
                # Append new data using pd.concat
                df = pd.concat([df, new_expense], ignore_index=True)
            else:
                # If no CSV file exists, new_expense becomes the DataFrame to save
                df = new_expense

            # Save the updated data to the CSV file
            df.to_csv("exp.csv", index=False)
            st.success("Expense added successfully!")
        else:
            st.error("Please fill all fields.")

    # Add a button to go back to the dashboard
    if st.button("Back to Dashboard"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()


def dashboard():
    st.markdown("<h1 style='color: #2c3e50;'>Financial Dashboard</h1>", unsafe_allow_html=True)

    if os.path.exists("exp.csv"):
        # Load the expense data
        df = pd.read_csv("exp.csv")

        # Total expenses
        total_expenses = df["Amount"].sum()

        # Display total expenses
        st.markdown("<h2 style='text-align: center;'>Overview</h2>", unsafe_allow_html=True)
        st.metric("Total Expenses", f"${total_expenses:,.2f}")

    # Divider line and quick navigation buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Quick Navigation</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Expense"):
            st.session_state["current_page"] = "add_expense"
            st.rerun()
    with col2:
        if st.button("View Expenses"):
            st.session_state["current_page"] = "view_expenses"
            st.rerun()

    # Display the pie chart below the "Quick Navigation" section
    if os.path.exists("exp.csv"):
        # Group expenses by category
        category_summary = df.groupby("Category")["Amount"].sum()

        # Set font size for pie chart labels and reduce the size of the pie chart
        plt.rcParams.update({'font.size': 8})  # Reduce font size for labels

        # Create a three-column layout and use the middle one for the pie chart
        col1, col2, col3 = st.columns([1, 2, 1])  # Adjust the widths of the columns for 1/3 in the middle

        with col2:  # The middle column takes 1/3 of the screen width
            st.markdown("<h3 style='text-align: center;'>Expenses by Category</h3>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(3, 3))  # Adjust the figure size
            ax.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis("equal")  # Equal aspect ratio ensures that the pie is drawn as a circle.
            st.pyplot(fig)


def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"
    
    if not st.session_state["logged_in"]:
        login()
    else:
        if st.session_state["current_page"] == "dashboard":
            dashboard()
        elif st.session_state["current_page"] == "add_expense":
            add_expense()
        elif st.session_state["current_page"] == "view_expenses":
            view_expenses()  # Ensure this is called for the "View Expenses" page

if __name__ == "__main__":
    main()