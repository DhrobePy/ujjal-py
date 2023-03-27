import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, time, timedelta, date
import base64
import streamlit_lottie as st_lottie
import requests
import json
import altair as alt
import plotly.express as px




with open('download_button.json', 'r') as f:
    button_data = f.read()

def create_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download Expense Report</a>'
    return href
    

def create_products_table():
    data = {
        'Product': ['Rutti','Jora Hati','Ek hati', 'Kobutor','sunflower','E-Atta'],
        'Description': ['Description 1', 'Description 2', 'Description 3', 'Description 4', 'Description 5', 'Description 6'],
        'Stock as of yesterday ': [50, 80, 25, 75, 60, 90],
        'Stock as of Today':[20,30,40,20,30,40],
        'Total Stock Remaining':[70, 110, 65, 95,90,130]
    }
    df = pd.DataFrame(data)
    return df
def collect_stock_data():
    st.title('Collect Stock Data')

    product_names = ['Rutti', 'Jora Hate', 'Single haiti', 'Kobutor', 'Sunflower', 'Elders Atta']
    stock_data = {}

    with st.form(key='stock_form'):
        for product_name in product_names:
            stock_data[product_name] = {
                'stock_amount': st.number_input(f"{product_name} Stock Amount", min_value=0, step=1),
                'yesterdays_stock': st.number_input(f"{product_name} Yesterday's Stock", min_value=0, step=1)
            }
        
        submit_button = st.form_submit_button('Save Stock Data')

    if submit_button:
        # Save the stock data to Firestore
        for product_name, stock_values in stock_data.items():
            product_ref = db.collection('products').document(product_name)
            product_ref.set(stock_values)
        st.success('Stock data saved successfully')

    # Display the updated stock table
    st.subheader('Updated Stock Table')
    stock_table_data = []
    for product_name in product_names:
        product_ref = db.collection('products').document(product_name)
        product_data = product_ref.get().to_dict()
        stock_amount = product_data.get('stock_amount', 0)
        yesterdays_stock = product_data.get('yesterdays_stock', 0)
        total_stock = stock_amount + yesterdays_stock
        stock_table_data.append({
            'Product': product_name, 
            'Stock Amount': stock_amount, 
            'Yesterday\'s Stock': yesterdays_stock,
            'Total Stock': total_stock
        })
    stock_df = pd.DataFrame(stock_table_data)
    st.write(stock_df)

    # Edit the stock table
    if st.button('Edit Stock Table'):
        st.write('Edit functionality not implemented yet')

def add_order(order_data):
    orders_ref = db.collection('orders')
    orders_ref.add(order_data)

def update_order(order_id, order_data):
    orders_ref = db.collection('orders')
    orders_ref.document(order_id).update(order_data)

def add_to_receivables(receivable_data):
    receivables_ref = db.collection('receivables')
    receivables_ref.add(receivable_data)


from datetime import datetime, time

def order_form():
    st.subheader("Add Order")
    product = st.text_input("Product")
    delivery_date = st.date_input("Delivery Date")
    delivery_datetime = datetime.combine(delivery_date, time())  # Convert date to datetime
    quotation_price = st.number_input("Quotation Price", value=0.0)
    quantity_50kg = st.number_input("Quantity in 50kg Bags", value=0)
    quantity_74kg = st.number_input("Quantity in 74kg Bags", value=0)
    customer = st.text_input("Customer Name")

    if st.button("Submit Order"):
        order_data = {
            "product": product,
            "delivery_date": delivery_datetime,  # Store the datetime object
            "quotation_price": quotation_price,
            "quantity_50kg": quantity_50kg,
            "quantity_74kg": quantity_74kg,
            "customer": customer,
        }
        add_order(order_data)
        st.success("Order added successfully!")


def orders_due_today():
    now = datetime.now()
    today_start = datetime.combine(now.date(), time())
    today_end = today_start + timedelta(days=1)

    orders_ref = db.collection("orders")
    orders = orders_ref.where("delivery_date", ">=", today_start).where("delivery_date", "<", today_end).stream()

    orders_list = []
    for order in orders:
        order_data = order.to_dict()
        order_data["id"] = order.id  # Add the order ID to the dictionary
        orders_list.append(order_data)

    due_orders = {}
    for order in orders_list:
        customer = order['customer']
        product = order['product']
        if customer not in due_orders:
            due_orders[customer] = {}

        if product not in due_orders[customer]:
            due_orders[customer][product] = order
        else:
            due_orders[customer][product]['quantity_50kg'] += order['quantity_50kg']
            due_orders[customer][product]['quantity_74kg'] += order['quantity_74kg']

    return due_orders


def customer_details_form():
    st.subheader("Customer Details")

    customer_name = st.text_input("Customer Name", "")
    region = st.text_input("Region", "")
    address = st.text_input("Address", "")
    contact_info = st.text_input("Contact Info", "")
    contract_status = st.selectbox("Contract Status", ["Active", "Inactive"])
    previous_due = st.number_input("Previous Due", 0)
    order_in_que = st.number_input("Order in Que", 0)
    total_receivables = st.number_input("Total Receivables", 0)

    if st.button("Save Customer Details"):
        customer_data = {
            "customer_name": customer_name,
            "region": region,
            "address": address,
            "contact_info": contact_info,
            "contract_status": contract_status,
            "previous_due": previous_due,
            "order_in_que": order_in_que,
            "total_receivables": total_receivables,
        }
        add_customer_to_database(customer_data)
        st.success("Customer details saved successfully.")

def add_customer_to_database(customer_data):
    db.collection("customers").add(customer_data)

def display_all_customer_details():
    st.subheader("All Customer Details")

    customer_data = get_all_customer_info()
    if customer_data:
        st.table(pd.DataFrame(customer_data))
    else:
        st.write("No customer details found.")

def get_all_customer_info():
    customers = db.collection("customers").stream()
    customer_data = [customer.to_dict() for customer in customers]
    return customer_data

def search_customer_by_name():
    search_name = st.text_input("Search by name", "")
    if search_name:
        customer_data = search_customer_data("customer_name", search_name)
        if customer_data:
            st.table(pd.DataFrame(customer_data))
        else:
            st.write("No customers found with this name.")

def search_customer_by_region():
    regions = get_all_regions()
    selected_region = st.selectbox("Select a region", regions)
    customer_data = search_customer_data("region", selected_region)
    if customer_data:
        st.table(pd.DataFrame(customer_data))
    else:
        st.write(f"No customers found in the {selected_region} region.")

def search_customer_data(field, value):
    customers = db.collection("customers").where(field, "==", value).stream()
    customer_data = [customer.to_dict() for customer in customers]
    return customer_data

def get_all_regions():
    customers = db.collection("customers").stream()
    regions = set(customer.to_dict()["region"] for customer in customers)
    return list(regions)




def order_due_form():
    st.subheader("Submit Order")

    customer_name = st.selectbox("Customer Name", get_customer_names())
    display_customer_info(customer_name)

    product = st.selectbox("Product", ["50kg bag", "74kg bag"])
    price_quotation = st.number_input("Price Quotation", 0)
    quantity = st.number_input("Quantity", 0)
    due_date = st.date_input("Order Due Date")
    payment_method = st.selectbox("Payment Method", ["Cash", "Credit"])

    if st.button("Submit Order"):
        order_data = {
            "customer_name": customer_name,
            "product": product,
            "price_quotation": price_quotation,
            "quantity": quantity,
            "due_date": due_date,
            "payment_method": payment_method,
        }
        submit_order_to_database(order_data)
        st.success("Order submitted successfully.")

def display_customer_info(customer_name):
    customer_info = get_customer_info(customer_name)
    if customer_info:
        st.table(pd.DataFrame(customer_info, index=[0]))

def get_customer_names():
    customers = db.collection("customers").stream()
    customer_names = [customer.to_dict()["customer_name"] for customer in customers]
    return customer_names

def get_customer_info(customer_name):
    customers = db.collection("customers").where("customer_name", "==", customer_name).stream()
    customer_info = None
    for customer in customers:
        customer_info = customer.to_dict()
        break
    return customer_info

def submit_order_to_database(order_data):
    db.collection("orders").add(order_data)


def customer_details():
    st.title('Customer Details')

    # Add a button to read the customer details from an Excel file
    # Add a button to read the customer details from an Excel file
    if st.button('Read Customer Details from Excel'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d-%m-%Y')
        df['Days Overdue'] = (datetime.now().date() - df['Due Date']).dt.days.clip(lower=0)
        df['Amount Due'] = df['Amount Due'].astype(float)
        df['Total Amount Due'] = df['Amount Due'].sum()
        df['Total Amount Due'] = df['Total Amount Due'].astype(float)
    
        # Show the table of customer details
        st.write(df)

    # Add a button to update the customer details
    if st.button('Update Customer Details'):
        # Show the table of customer details with editable cells
        editable_df = df.copy()
        editable_df.set_index('Customer Name', inplace=True)
        st.write(editable_df)

        # Add a button to save the updated customer details
        if st.button('Save Customer Details'):
            # Update the customer details in the Excel file
            editable_df.reset_index(inplace=True)
            editable_df.to_excel('customer_details.xlsx', index=False)

# Add a button to show the table of receivables
    if st.button('Show Receivables'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d-%m-%Y')
        df['Days Overdue'] = (datetime.now().date() - df['Due Date']).dt.days.clip(lower=0)
        df['Amount Due'] = df['Amount Due'].astype(float)
    
        # Show the table of receivables
        receivables_df = df[['Customer Name', 'Due Date', 'Amount Due', 'Days Overdue']]
        st.write(receivables_df)

    # Add a button to update the receivables
    if st.button('Update Receivables'):
        # Show the table of receivables with editable cells
        editable_df = receivables_df.copy()
        editable_df.set_index('Customer Name', inplace=True)
        st.write(editable_df)

        # Add a button to save the updated receivables
        if st.button('Save Receivables'):
            # Update the receivables in the Excel file
            editable_df.reset_index(inplace=True)
            editable_df.to_excel('customer_details.xlsx', index=False)

# Add a button to show the total amount due
    if st.button('Show Total Amount Due'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Amount Due'] = df['Amount Due'].astype(float)
    
        # Show the total amount due
        total_amount_due = df['Amount Due'].sum()
        st.write(f'Total Amount Due: {total_amount_due}')
    
    # Add a button to show customer-wise total bills due
    
    if st.button('Show Customer-wise Total Bills Due'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Amount Due'] = df['Amount Due'].astype(float)
    
    # Group the customer details by customer name and show the total bills due for each customer
    customer_groups = df.groupby('Customer Name')
    for customer_name, customer_df in customer_groups:
        total_bills_due = customer_df['Amount Due'].sum()
        st.write

def display_stock_table():
    st.subheader('Stock Table')
    product_refs = db.collection('products').get()
    product_names = [product_ref.id for product_ref in product_refs]

    stock_table_data = []
    for product_name in product_names:
        product_ref = db.collection('products').document(product_name)
        product_data = product_ref.get().to_dict()
        stock_amount = product_data.get('stock_amount', 0)
        yesterdays_stock = product_data.get('yesterdays_stock', 0)
        total_stock = stock_amount + yesterdays_stock
        stock_table_data.append({
            'Product': product_name,
            'Stock Amount': f"{stock_amount} Kg",
            'Yesterday\'s Stock': f"{yesterdays_stock} Kg",
            'Total Stock': f"{total_stock} Kg"
        })
    stock_df = pd.DataFrame(stock_table_data)
    st.write(stock_df)

def edit_stock():
    with st.form(key='edit_stock_form'):
        product_names = [product_ref.id for product_ref in db.collection('products').get()]
        selected_product_name = st.selectbox('Select a product to edit', options=product_names)

        product_ref = db.collection('products').document(selected_product_name)
        product_data = product_ref.get().to_dict()

        stock_amount = st.number_input(f"{selected_product_name} Stock Amount", min_value=0, step=1, value=product_data.get('stock_amount', 0))
        yesterdays_stock = st.number_input(f"{selected_product_name} Yesterday's Stock", min_value=0, step=1, value=product_data.get('yesterdays_stock', 0))

        submit_button = st.form_submit_button('Save Edited Stock Data')

    if submit_button:
        product_ref.set({
            'stock_amount': stock_amount,
            'yesterdays_stock': yesterdays_stock
        })
        st.success('Stock data updated successfully')
        display_stock_table()

def add_product():
    with st.form(key='add_product_form'):
        new_product_name = st.text_input('Enter new product name')
        stock_amount = st.number_input('Stock Amount', min_value=0, step=1)
        yesterdays_stock = st.number_input('Yesterday\'s Stock', min_value=0, step=1)
        submit_button = st.form_submit_button('Add New Product')

    if submit_button:
        product_ref = db.collection('products').document(new_product_name)
        product_ref.set({
            'stock_amount': stock_amount,
            'yesterdays_stock': yesterdays_stock
        })
        st.success('New product added successfully')
        display_stock_table()


def show_add_customer_form():
    st.write("Add a New Customer")
    customer_details_form()

def get_customer_info(customer_name):
    customers = db.collection("customers").where("customer_name", "==", customer_name).stream()
    customer_info = None
    for customer in customers:
        customer_info = customer.to_dict()
        customer_info["id"] = customer.id  # Add the document ID to the customer_info dictionary
        break
    return customer_info
def show_edit_customer_form():
    st.write("Edit Customer Details")
    customer_name = st.selectbox("Select a Customer", get_customer_names())
    customer_info = get_customer_info(customer_name)
    if customer_info:
        edit_customer_details(customer_info)
    else:
        st.write("No customer found with this name.")

def edit_customer_details(customer_info):
    customer_id = customer_info['id']
    customer_name = st.text_input("Customer Name", customer_info['customer_name'])
    region = st.text_input("Region", customer_info['region'])
    address = st.text_input("Address", customer_info['address'])
    contact_info = st.text_input("Contact Info", customer_info['contact_info'])
    contract_status = st.selectbox("Contract Status", ["Active", "Inactive"], index=("Active" == customer_info['contract_status']))
    previous_due = st.number_input("Previous Due", value=customer_info['previous_due'])
    order_in_que = st.number_input("Order in Que", value=customer_info['order_in_que'])
    total_receivables = st.number_input("Total Receivables", value=customer_info['total_receivables'])

    if st.button("Update Customer Details"):
        updated_customer_data = {
            "customer_name": customer_name,
            "region": region,
            "address": address,
            "contact_info": contact_info,
            "contract_status": contract_status,
            "previous_due": previous_due,
            "order_in_que": order_in_que,
            "total_receivables": total_receivables,
        }
        update_customer_in_database(customer_id, updated_customer_data)
        st.success("Customer details updated successfully.")

def update_customer_in_database(customer_id, updated_customer_data):
    db.collection("customers").document(customer_id).update(updated_customer_data)






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
    choice = option_menu(
        options=['Products', 'List of Clients','Prices', 'Orders Due', 'Bills Receivables', 'Bills Payables'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal')
    

    # Show the appropriate section based on the user's choice
    if choice == 'Products':
        st.write('Here you can view a list of all products')
        #collect_stock_data()
        display_stock_table()
        if st.button('Edit Stock'):
            edit_stock()
        if st.button('Add More Types of Products into Inventory'):
            add_product()


    elif choice == 'List of Clients':
        st.header('List of Clients')
        client_filter = st.selectbox("Filter by", ["Name", "Region", "All"])
        if client_filter == "Name":
            search_customer_by_name()
        elif client_filter == "Region":
            search_customer_by_region()
        else:
            display_all_customer_details()
        if st.button("Add Customer"):
            show_add_customer_form()
        if st.button("Edit Customer Details"):
            show_edit_customer_form()

        
    elif choice == 'Prices':
        st.header('Prices')
        st.write('Here you can view and update prices for different products')
    
    elif choice=='Bills Receivables':
        st.header('Bills receivables')
        customer_details_form()
        display_all_customer_details()

    elif choice == 'Orders Due':
        st.header('Orders Due')
        st.write('Here you can view a list of all pending orders')
        order_due_form()

    

    #elif choice == 'Orders Due':
        #st.header('Orders Due')
        #st.write('Here you can view a list of all pending orders')
    #elif choice=='Bills Receivables':
        #st.header('Bills receivables')
        #customer_details()
    elif choice == 'Bills Payables':
        st.header('Bills Due')
        st.write('Here you can view a list of all pending bills')

def create_chart(df):
    chart_data = df.groupby('Category')['Amount'].sum()
    chart = alt.Chart(chart_data.reset_index()).mark_bar().encode(
        x=alt.X('Category', sort='-y'),
        y=alt.Y('Amount', title='Total Amount'),
        tooltip=['Category', 'Amount']
    ).properties(
        title='Expenses by Category'
    )
    return chart


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
    

    elif selected == 'Update Records':
        st.header('Update Records')

    # Retrieve all expenses from Firestore and create a dictionary
        def get_expenses():
            expenses = {}
            for expense in db.collection('expenses').get():
                expense_id = expense.id
                data = expense.to_dict()
                expenses[expense_id] = data
            return expenses

    # Display the expenses as a drop-down menu
        expenses = get_expenses()
        expense_ids = list(expenses.keys())
        expense_names = [f"{expense['category']} - {expense['expense_date']}" for expense in expenses.values()]
        expense_dict = dict(zip(expense_ids, expense_names))
        selected_expense_id = st.selectbox("Select an expense to update", options=expense_ids, format_func=lambda x: expense_dict[x])

    # Get the selected expense's details
        selected_expense = expenses[selected_expense_id]

    # Show the selected expense's details in a form, allowing users to edit the values
        category = st.selectbox('Category of Expense', ['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'], index=['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'].index(selected_expense['category']))
        amount = st.number_input('Amount of Expense', value=float(selected_expense['amount']))
        method = st.selectbox('Way of Payment', ['Cash', 'Bank Account Cheque'], index=['Cash', 'Bank Account Cheque'].index(selected_expense['method']))
        if method == 'Cash':
            paid_by = st.text_input('Paid By', value=str(selected_expense.get('paid_by', '')))
        else:
            bank_accounts = ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234']
            paid_by = st.selectbox('Bank Account Number', bank_accounts, index=bank_accounts.index(str(selected_expense.get('paid_by', ''))))
        remarks = st.text_area('Remarks', value=str(selected_expense.get('remarks', '')))
        expense_date = st.date_input('Date of Expense', value=datetime.strptime(selected_expense['expense_date'], '%Y-%m-%d').date())

    # Update the selected expense in the Firestore database with the new values from the form
        if st.button('Update Expense'):
            expense_ref = db.collection('expenses').document(selected_expense_id)
            expense_date_str = expense_date.strftime('%Y-%m-%d')
            expense_ref.update({
            'category': category,
            'amount': amount,
            'method': method,
            'paid_by': paid_by,
            'remarks': remarks,
            'expense_date': expense_date_str,
        })
            st.success('Expense updated successfully')

    
    
    elif selected == 'Expense Summary':
        st.header('Expense Summary')

    # Add date pickers to select start and end dates
        start_date = st.date_input('Select start date')
        end_date = st.date_input('Select end date', value=datetime.now().date())

    # Add a button to show expenses for the selected period
        if st.button('Show Expense Report'):
        # Define a function to retrieve expense data from the Firestore collection
            def get_expenses():
                expenses = []
                for expense in db.collection('expenses').get():
                    data = expense.to_dict()
                    if 'method' in data:
                        expense_date_str = data.get('expense_date', '')
                        expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date() if expense_date_str else None
                        if expense_date and start_date <= expense_date <= end_date:
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
                df = df.append({'Category': 'Total', 'Amount': total_amount}, ignore_index=True)
        
                # Group the expenses by category and show a summary table for each category
                categories = df['Category'].unique()
                for category in categories:
                    if category == 'Total':
                        continue
                    category_df = df[df['Category'] == category]
                    st.subheader(f'{category} Expenses')
                    st.write(category_df)
                    st.write(f'Total Amount: {category_df["Amount"].sum()}')

                # Show the summary table for all expenses
                st.subheader('All Expenses')
                st.dataframe(df)

                expenses_chart_data =df[df['Category'] != 'Total']
                chart = create_chart(expenses_chart_data)
                fig = px.pie(df, values='Amount', names=df.index)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.altair_chart(chart, use_container_width=True)
                with col2:
                    st.plotly_chart(fig)           
                


                # Add a button to download the expense report as a CSV file
                #st.button("Download Expense Summary Report"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download Expense Report (CSV)</a>'
                st.markdown(href, unsafe_allow_html=True)

            # Retrieve the expense data for the selected period and display it as a table
            get_expenses()



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
