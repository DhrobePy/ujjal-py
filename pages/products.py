import streamlit as st
from streamlit_lottie import st_lottie
import json

st.write("Fuck You")

st.sidebar.header("Fuck YOu Too")

def load_lottiefile(path:str):
    with open (path,"r")as f:
        return json.load(f)

welcome_animation2=load_lottiefile("/Users/Dhrobe/Desktop/Ujjal/2nd.json")
st_lottie(welcome_animation2)
