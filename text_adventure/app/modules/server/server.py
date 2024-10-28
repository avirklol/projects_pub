
import os
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = f"mongodb+srv://annandvirk:{json.loads(os.getenv('MONGO_DB'))['password']}@text-adventure.fnvfw.mongodb.net/?retryWrites=true&w=majority&appName=text-adventure"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
