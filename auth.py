import bcrypt
from pymongo import MongoClient

# Connect to your MongoDB database
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client.loss_ratio
collection = db.dashboard_users

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# List of user details
users = [
    {"username": "Dorcas", "password": "Dorcas123"},
    {"username": "Tshepo", "password": "Tshepo123"},
    {"username": "Innocent", "password": "Innocent123"},
    {"username": "Bruce", "password": "Bruce123"},
    {"username": "Penny", "password": "Penny123"},
    {"username": "Francis", "password": "Francis123"}
]

# Hash the passwords and store the users in the collection
for user in users:
    hashed_password = hash_password(user["password"])
    user["password"] = hashed_password
    collection.insert_one(user)

print("Users created successfully.")
