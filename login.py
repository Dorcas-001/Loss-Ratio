import streamlit as st
import pymongo
import bcrypt

# MongoDB connection string
mongo_uri = "mongodb://localhost:27017/"
client = pymongo.MongoClient(mongo_uri)
db = client.loss_ratio
collection = db.dashboard_users

# Function to verify a password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def login(username, password):
    user = collection.find_one({"username": username})
    if user and verify_password(user['password'], password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Logged in successfully!")
    else:
        st.error("Invalid username or password")

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    login(username, password)
