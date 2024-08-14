from pymongo import MongoClient
import os

MONGO_URI = os.getenv('MONGO_URI','mongodb://localhost:27017/todo_db')
if not MONGO_URI:
    raise EnvironmentError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client['todo_db']
tasks_collection = db['tasks']
users_collection = db['users']