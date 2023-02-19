import streamlit as st
#from streamlit_lottie import st_lottie
import requests
import json


st.title(' .........Hello!!!!.......')

def load_lottiefile(path:str):
    with open (path, "r") as f:
        return json.load(f)

#load_file=load_lottiefile("hello.json")
#load_2nd=load_lottiefile("/Users/Dhrobe/Desktop/Ujjal/2nd.json")

st_lottie(load_file)
        
    
# Load the user data from the JSON file
with open("users.json") as f:
    user_data = json.load(f)

def check_credentials(username, password):
    for user in user_data:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def second_page():
    st_lottie(load_2nd)
    

def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username, password):
            st.success(second_page)
        else:
            st.error("Invalid username or password")

# Render the login form
login()


# Render the appropriate page based on the user's login status



















