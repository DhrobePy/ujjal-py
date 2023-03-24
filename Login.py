import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, time



cred = credentials.Certificate("expenses_updated.json")
#firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()


import pandas as pd



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
    #st.write('Navigation')
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
    selected = option_menu(
        options=['Add Expense', 'Update Records', 'Expense Summary'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal')

    # Show the appropriate section based on the user's choice
    if selected == 'Add Expense':
        st.header('Add Expense')
        expense_date = st.date_input('Date of Expense')
        expense_date_str = expense_date.strftime('%Y-%m-%d')

        # Define a function to insert expense data into the Firestore collection
        # Define a function to insert expense data into the Firestore collection
        def insert_data(category, amount, method, paid_by, remarks, expense_date):
            expense_date_str = expense_date.strftime('%Y-%m-%d')
            now = datetime.now()
            db.collection('expenses').add({
                'category': category,
                'amount': amount,
                'method': method,
                'paid_by': paid_by,
                'remarks': remarks,
                'expense_date': expense_date_str,
                'datetime': now
            })


        # Add a form for the user to enter expense details
        category = st.selectbox('Category of Expense', ['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'])
        amount = st.number_input('Amount of Expense')
        method = st.selectbox('Way of Payment', ['Cash', 'Bank Account Cheque'])
        if method == 'Cash':
            paid_by = st.text_input('Paid By')
        else:
            bank_accounts = ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234']
            paid_by = st.selectbox('Bank Account Number', bank_accounts)

        remarks = st.text_area('Remarks')

        # Add a button to submit the form and insert the data into the Firestore collection
        if st.button('Add Expense'):
            insert_data(category, amount, method, paid_by, remarks, expense_date)
            st.success('Expense added successfully')
    

    elif selected == 'Expense Summary':
        st.header('Expense Summary')

        # Define a function to retrieve expense data from the Firestore collection
        # Define a function to retrieve expense data from the Firestore collection
        def get_expenses():
            expenses = []
            for expense in db.collection('expenses').get():
                data = expense.to_dict()
                if 'method' in data:
                    expense_date_str = data.get('expense_date', '')
                    expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date() if expense_date_str else None
                    expenses.append({
                        'Category': data['category'],
                        'Amount': data['amount'],
                        'Payment Method': data['method'],
                        'Paid By': data.get('paid_by', ''),
                        'Description': data.get('remarks', ''),
                        'Date of Expense': expense_date
                    })
            df = pd.DataFrame(expenses)
            total_amount = df['Amount'].sum()
            df = df.append({'category': 'Total', 'amount': total_amount}, ignore_index=True)
    
    # Group the expenses by category and show a summary table
            #summary_df = df.groupby('category')['amount'].sum()
            return df


        # Retrieve the expense data and display it as a table
        expenses_df = get_expenses()
        st.dataframe(expenses_df)

       




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
    #st.write('Navigation')

    selected=option_menu(
        menu_title=None,
        options = ['Home', 'Expense', 'Costing and Pricing', 'Balance Sheet'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal',
        )
        
    #choice = st.radio('', options)

    # Show the appropriate app section based on the user's choice
    if selected == 'Home':
        home()
    elif selected == 'Expense':
        expense()
    elif selected == 'Costing and Pricing':
        costing_pricing()
    elif selected == 'Balance Sheet':
        balance_sheet()
