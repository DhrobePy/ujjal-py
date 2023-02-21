import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json


st.title(' Welcome to Ujjal Flour Mills Dashboard')

def load_lottiefile(path:str):
    with open (path, "r") as f:
        return json.load(f)

load_file=load_lottiefile("/app/ujjal-py/hello.json")
#load_2nd=load_lottiefile("/Users/Dhrobe/Desktop/Ujjal/2nd.json")

st_lottie(load_file)
        

def authenticate(username,password):
    if username=='ziead' and password=='123ziead':
        return True
    elif username=='dhrobe' and password=='123dhrobe':
        return True
    else:
        return False
st.sidebar.title("Login")

username=st.sidebar.text_input("Enter Username")
password=st.sidebar.text_input("Enter Password")

if st.sidebar.button("Login"):
    if authenticate(username,password):
        st.sidebar.success("Logged in as {}".format(username))
    else:
        st.sidebar.error("Incorrect username or password")


# Render the appropriate page based on the user's login status



















