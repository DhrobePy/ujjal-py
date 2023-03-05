import streamlit as st

# Define username and password
CORRECT_USERNAME = 'myusername'
CORRECT_PASSWORD = 'mypassword'

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
    st.write('Welcome to the Home section of the app')

def expense():
    st.title('Expense')
    st.write('Welcome to the Expense section of the app')

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
    # Add a horizontal navigation bar
    st.set_page_config(page_title='App', page_icon=':money_with_wings:')
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
