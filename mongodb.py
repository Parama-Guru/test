import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

load_dotenv()

def connect_mongodb():
    try:
        uri = os.getenv('MONGODB_URI')
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        db = client["lassie"]
        collection = db["user_login"]
        return collection
    except Exception as e:
        print(e)
