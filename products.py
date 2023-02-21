import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests
from datetime import datetime
import time


st.title("All the products")


#showing the animation in welcoe screen

def load_lottiefile(path:str):
    with open (path,"r")as f:
        return json.load(f)

welcome_animation=load_lottiefile("/Users/Dhrobe/Desktop/Ujjal/products.json")

st_lottie(welcome_animation)

#sidebar stars here

