from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pymongo import MongoClient

# Load environment variables from the .env file
load_dotenv()

# Create a MongoDB client
client = MongoClient(os.getenv("MONGODB_URL"))

# Connect to the cream-card database
db = client['cream-card']

# print(db.list_collection_names())

# Fetch everything from the inventories collection
inventories_collection = db['inventories']

users_collection = db['users']

subscriptions_collection = db['subscriptionplans']


# for item in users_collection.find():
#     print(item.address)


# Retrieve all documents in the inventories collection
all_inventories = inventories_collection.find({}, {'embedding': 0})

count = 0
for item in all_inventories:
    print(item)

    count+=1

print('total inventories:',count)


