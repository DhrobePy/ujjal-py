import streamlit as st
from streamlit_lottie import st_lottie
import json

st.write("This is where all products goes")

st.sidebar.header("Category")

def load_lottiefile(path:str):
    with open (path,"r")as f:
        return json.load(f)

welcome_animation2=load_lottiefile("/app/ujjal-py/pages/products.json")
st_lottie(welcome_animation2)
