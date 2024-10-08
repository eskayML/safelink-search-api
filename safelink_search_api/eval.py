from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Create a MongoDB client
client = MongoClient(os.getenv("MONGODB_URL"))

# Connect to the cream-card database
db = client['cream-card']

# Fetch everything from the inventories collection
inventories_collection = db['inventories']

# Retrieve all documents in the inventories collection
all_inventories = inventories_collection.find()

for item in all_inventories:
    print(item)