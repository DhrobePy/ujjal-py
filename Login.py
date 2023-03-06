import streamlit as st
import sqlite3


import pandas as pd

#To hide Header & Footer of Streamlit APP"
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



# Define username and password
CORRECT_USERNAME = 'Ujjaladmin'
CORRECT_PASSWORD = 'admin101'

# Define the login page
def login():
    # Add a title
    st.title('Login')

    # Add a form with username and password inputs
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    # Add a button to submit the form
    if st.button('Login'):
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            # Set the session state to True
            st.session_state.logged_in = True
        else:
            st.error('Incorrect username or password')

# Define the app sections
def home():
    st.title('Home')

    # Add a horizontal navigation bar for the Home page
    st.write('Navigation')
    options = ['Products', 'Prices', 'Order Due', 'Bills Due']
    choice = st.radio('', options)

    # Show the appropriate section based on the user's choice
    if choice == 'Products':
        st.header('Products')
        st.write('Here you can view a list of all products')
    elif choice == 'Prices':
        st.header('Prices')
        st.write('Here you can view and update prices for different products')
    elif choice == 'Order Due':
        st.header('Order Due')
        st.write('Here you can view a list of all pending orders')
    elif choice == 'Bills Due':
        st.header('Bills Due')
        st.write('Here you can view a list of all pending bills')

def expense():
    st.title('Expense')

    # Add a horizontal navigation bar for the Expense section
    st.write('Navigation')
    options = ['Add Expense', 'Update Records', 'Export Summary']
    choice = st.radio('', options)

    # Show the appropriate section based on the user's choice
    if choice == 'Add Expense':
        st.header('Add Expense')

        # Define a function to insert expense data into the database
        def insert_data(category, amount, date, remarks):
            conn = sqlite3.connect('expense_tracker.db')
            c = conn.cursor()
            c.execute("INSERT INTO expenses_tracker (category, amount, date, remarks) VALUES (?, ?, ?, ?)", (category, amount, date, remarks))
            conn.commit()
            conn.close()

        # Add a form for the user to enter expense details
        category = st.selectbox('Category of Expense', ['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'])
        amount = st.number_input('Amount of Expense')
        date = st.date_input('Date of Expenditure')
        remarks = st.text_area('Remarks')

        # Add a button to submit the form and insert the data into the database
        if st.button('Add Expense'):
            insert_data(category, amount, date, remarks)
            st.success('Expense added successfully')

    elif choice == 'Update Records':
        st.header('Update Records')
        st.write('Here you can update existing expense records')
    elif choice == 'Export Summary':
        st.header('Export Summary')
        st.write('Here you can export a summary of all expense records')


def costing_pricing():
    st.title('Costing and Pricing')
    st.write('Welcome to the Costing and Pricing section of the app')

def balance_sheet():
    st.title('Balance Sheet')
    st.write('Welcome to the Balance Sheet section of the app')

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Show the appropriate page based on the logged-in state
if not st.session_state.logged_in:
    login()
else:
    # Add a horizontal navigation bar for the app sections
    #st.set_page_config(page_title='App', page_icon=':money_with_wings:')
    st.write('Navigation')
    options = ['Home', 'Expense', 'Costing and Pricing', 'Balance Sheet']
    choice = st.radio('', options)

    # Show the appropriate app section based on the user's choice
    if choice == 'Home':
        home()
    elif choice == 'Expense':
        expense()
    elif choice == 'Costing and Pricing':
        costing_pricing()
    elif choice == 'Balance Sheet':
        balance_sheet()
