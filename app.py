import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Financial Dashboard", layout="wide")

def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def authenticate_user(username, password):
    user_df = pd.read_csv('user_details.csv')
    user = user_df[(user_df['Login'] == username) & (user_df['Password'] == password)]
    
    if not user.empty:
        st.session_state["user_id"] = user["UserID"].values[0]  # Store Userid in session
        return True
    return False

# Login form 
def login():
    st.markdown("<h1 style='color: #2c3e50;text-align: center;'>Expense Tracker Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center;'>Enter your credentials to access the dashboard.</p>", unsafe_allow_html=True)
        with st.form(key="login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            signup_button= st.form_submit_button("Signup")
        
        if login_button:
            if username and password:
                # Authenticating using the CSV file
                if authenticate_user(username, password):
                    st.success("Login successful!")
                    st.session_state["logged_in"] = True
                    st.session_state["current_page"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")

        if signup_button:

            st.session_state["current_page"] = "signup"
            st.rerun()

            
FILE_NAME = "user_details.csv"

def get_next_user_id():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        df = pd.read_csv(FILE_NAME)
        return df["UserID"].max() + 1 if not df.empty else 1
    return 1    
    

def save_to_csv(user_data):
    file_exists = os.path.exists(FILE_NAME)

    try:
        # Convert dict to df
        new_df = pd.DataFrame(user_data)

        # Append
        if file_exists and os.path.getsize(FILE_NAME) > 0:
            new_df.to_csv(FILE_NAME, mode="a", header=False, index=False, encoding="utf-8")
        else:
            new_df.to_csv(FILE_NAME, mode="w", header=True, index=False, encoding="utf-8")

        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def sign_up():
    st.markdown("<h1 style='color: #2c3e50;text-align: center;'>Create an Account</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center;'>Fill in the details to register.</p>", unsafe_allow_html=True)
        with st.form(key="signup_form"):
            next_user_id = get_next_user_id()

            name = st.text_input("Enter your name")
            email = st.text_input("Enter your email")
            phone_number = st.text_input("Enter your phone number")
            login = st.text_input("Enter your login")
            password = st.text_input("Enter your password", type="password")
            submit_button = st.form_submit_button("Signup")

            if submit_button:
                if name and email and phone_number and login and password:
                    user_data = {
                        "UserID": [next_user_id],
                        "Name": [name],
                        "Email": [email],  
                        "PhoneNumber": [phone_number],
                        "Login": [login],
                        "Password": [password]
                    }

                    if save_to_csv(user_data):
                        st.success(f"User {name} registered successfully with UserID {next_user_id}!")
                        st.session_state["current_page"] = "login"
                        st.rerun()
                    else:
                        st.error("Error saving data. Please try again.")
                else:
                    st.error("Please fill all fields.")

    if st.button("Back to Login"):
        st.session_state["current_page"] = "login"
        st.rerun()

def view_expenses():
    if "user_id" not in st.session_state:
        st.error("You need to log in first!")
        return

    user_id = st.session_state["user_id"]  

    if os.path.exists("exp.csv"):
        df = pd.read_csv("exp.csv")

        # Filter only the logged-in user's expenses
        user_expenses = df[df["UserID"] == user_id]

        if user_expenses.empty:
            st.warning("No expenses found for your account.")
        else:
            st.markdown("<h2 style='text-align: center;'>Your Expenses</h2>", unsafe_allow_html=True)
            st.table(user_expenses)  
    else:
        st.warning("No expenses found. Add some expenses to view them here.")

# edit or delete
    st.markdown("<h3 style='text-align: center;'>Edit or Delete Expense</h3>", unsafe_allow_html=True)
    row_to_edit_or_delete = st.number_input("Select Row Number to Edit or Delete", min_value=0, max_value=len(df) - 1, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit Selected Row"):
                st.session_state["row_to_edit"] = row_to_edit_or_delete
                st.session_state["edit_mode"] = True
    with col2:
        if st.button("Delete Selected Row"):
                # Delete selected row
                df = df.drop(row_to_edit_or_delete).reset_index(drop=True)
                df.to_csv("exp.csv", index=False)
                st.success(f"Row {row_to_edit_or_delete} deleted successfully!")
                st.rerun()  

        # Edit form 
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
                    # Update df
                    df.loc[row_to_edit_or_delete, "Amount"] = amount
                    df.loc[row_to_edit_or_delete, "Category"] = category
                    df.loc[row_to_edit_or_delete, "Date"] = date.strftime('%Y-%m-%d')
                    df.loc[row_to_edit_or_delete, "Time"] = time

                    # Save df to csv
                    df.to_csv("exp.csv", index=False)
                    st.success("Expense updated successfully!")
                    del st.session_state["edit_mode"]  
                    st.rerun()

                if cancel_button:
                    del st.session_state["edit_mode"]  
                    st.rerun()

    if st.button("Back to Dashboard"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()

def add_expense():
    st.markdown("<h2 style='text-align: center;'>Add Expense</h2>", unsafe_allow_html=True)

    if "user_id" not in st.session_state:
        st.error("You need to log in before adding expenses!")
        return

    user_id = st.session_state["user_id"]  

    with st.form(key="expense_form"):
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
        date = st.date_input("Date", value=datetime.today())
        submit_button = st.form_submit_button("Add Expense")

    if submit_button:
        if amount > 0 and category and date:
            current_time = datetime.now().strftime('%H:%M:%S')

            
            new_expense = pd.DataFrame({
                "UserID": [user_id],  
                "Amount": [amount],
                "Category": [category],
                "Date": [date.strftime('%Y-%m-%d')],
                "Time": [current_time]
            })

            if os.path.exists("exp.csv"):
                df = pd.read_csv("exp.csv")
                df = pd.concat([df, new_expense], ignore_index=True)
            else:
                df = new_expense

            df.to_csv("exp.csv", index=False)
            st.success(f"Expense added successfully for User {user_id}!")
        else:
            st.error(" lease fill all fields.")

    if st.button("Back to Dashboard"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()

def dashboard():
    if "user_id" not in st.session_state:
        st.error("You need to log in first!")
        return

    user_id = st.session_state["user_id"]  

    st.markdown("<h1 style='color: #2c3e50;'>Financial Dashboard</h1>", unsafe_allow_html=True)

    if os.path.exists("exp.csv"):
        df = pd.read_csv("exp.csv")

        user_expenses = df[df["UserID"] == user_id]

        if user_expenses.empty:
            st.warning("No expenses found for your account.")
            return  # Stop execution if no expenses are found

        # Total expenses for this user
        total_expenses = user_expenses["Amount"].sum()

        st.markdown("<h2 style='text-align: center;'>Overview</h2>", unsafe_allow_html=True)
        st.metric("Total Expenses", f"${total_expenses:,.2f}")

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

        # Generate pie chart
        category_summary = user_expenses.groupby("Category")["Amount"].sum()

        if not category_summary.empty:
            plt.rcParams.update({'font.size': 8})  

            col1, col2, col3 = st.columns([1, 2, 1])  
            with col2:  
                st.markdown("<h3 style='text-align: center;'>Your Expenses by Category</h3>", unsafe_allow_html=True)
                fig, ax = plt.subplots(figsize=(3, 3))  
                ax.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.axis("equal")  
                st.pyplot(fig)

    else:
        st.warning("No expenses recorded yet. Start adding some expenses!")

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"
    
    if not st.session_state["logged_in"]:
        if st.session_state["current_page"] == "login":
            login()
        elif st.session_state["current_page"] == "signup":
            sign_up()
    else:
        if st.session_state["current_page"] == "dashboard":
            dashboard()
        elif st.session_state["current_page"] == "add_expense":
            add_expense()
        elif st.session_state["current_page"] == "view_expenses":
            view_expenses()


if __name__ == "__main__":
    main()
