import bcrypt
from pymongo import MongoClient
import streamlit as st

# MongoDB setup
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client.loss_ratio
collection = db.dashboard_users

# Function to authenticate user
def authenticate(username, password):
    user = collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False

# Function to render the login page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.current_page = "loss_ratio"
        else:
            st.error("Invalid username or password")
