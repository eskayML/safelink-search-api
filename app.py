from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import numpy as np, ast
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
import os
from pymongo import MongoClient
from supabase import create_client, Client
from utils import extract_text_from_image,fetch_and_convert_image_to_base64,generate_embedding
from bson import json_util
from flask_cors import CORS
from langchain_core.tools import tool
from bson.objectid import ObjectId
from docs import SWAGGER_TEMPLATE



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)
CORS(app)

# Create a MongoDB client
client = MongoClient(os.getenv("MONGODB_URL"))

# Connect to the cream-card database
db = client['cream-card']

# Fetch everything from the inventories collection
inventories_collection = db['inventories']
users_collection = db['users']


# Retrieve all documents in the inventories collection
all_inventories = inventories_collection.find()



# Swagger setup
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Embedding API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Swagger JSON Specification
@app.route("/static/swagger.json")
def swagger_spec():
    return jsonify(SWAGGER_TEMPLATE)





@tool
def is_inventory(query:str) -> str:
    """
    checks if the input string is trying to ask for a product or inventory
    """
    return "inventory"


@tool
def is_vendor(query:str) -> str:
    """
    checks if the input string is trying to ask for a vendor
    """
    return "vendor"



llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
tools = [is_inventory,is_vendor]
llm_with_tools = llm.bind_tools(tools, tool_choice = 'any')




@app.route('/search', methods=['POST'])
def search():
    try:
        # Get the search query from the request
        data = request.form
        query = data.get('query')

        query_target = llm_with_tools.invoke(query).tool_calls[0]['name']
        print(query_target)
        
        if not query:
            return jsonify({'status': 'error', 'message': 'No query provided'}), 400
        
        # Generate an embedding for the query
        query_embedding = generate_embedding(query)
        
        if query_embedding is None:
            return jsonify({'status': 'error', 'message': 'Error generating embedding'}), 500
        
        # Fetch all documents with embeddings from the MongoDB collection
        all_inventories = inventories_collection.find({'embedding': {'$exists': True}})
        
        # Prepare to store the similarity results
        results = []
        
        for inventory in all_inventories:
            inventory_embedding = inventory.get('embedding')
            
            if inventory_embedding:
                # Calculate cosine similarity between query embedding and inventory embedding
                similarity = cosine_similarity([query_embedding], [inventory_embedding])[0][0]
                
                # Create a copy of the inventory without the embedding
                inventory_without_embedding = {k: v for k, v in inventory.items() if k != 'embedding'}
                
                # Add the cleaned inventory and similarity score to the results list (for sorting purposes)
                results.append({
                    'inventory': inventory_without_embedding,  # Store the document without the embedding
                    'similarity_score': similarity  # Keep the score just for sorting
                })
        
        # Sort results by similarity score in descending order
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)[:5]
        
        # Extract the sorted inventory documents (without similarity score)
        sorted_inventories = [result['inventory'] for result in results]
        
        # Serialize the results using bson's json_util to handle ObjectId and other MongoDB types
        return json_util.dumps(sorted_inventories), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/add_inventory_to_ai', methods=['POST'])
def add_inventory_to_ai():
    """
    Generate an embedding for a specific inventory item, update the MongoDB document,
    and add the owner's profile picture (or an empty string if not available).
    """
    try:
        # Parse JSON payload
        data = request.form

        if not data or 'inventory_id' not in data:
            return jsonify({'status': 'error', 'message': 'Missing inventory_id in the request body'}), 400

        inventory_id = data['inventory_id']

        # Validate the inventory ID format
        if not ObjectId.is_valid(inventory_id):
            return jsonify({'status': 'error', 'message': 'Invalid inventory ID'}), 400

        # Retrieve the inventory item from the database
        inventory = inventories_collection.find_one({'_id': ObjectId(inventory_id)})

        if not inventory:
            return jsonify({'status': 'error', 'message': 'Inventory item not found'}), 404

        # Combine relevant fields to create a text representation for embedding
        inventory_text = ' '.join(str(value) for key, value in inventory.items() if key in ['title', 'description', 'price', 'currency'])

        # Generate the embedding
        embedding = generate_embedding(inventory_text)

        if embedding is None:
            return jsonify({'status': 'error', 'message': 'Error generating embedding'}), 500

        # Retrieve the owner's profile picture
        owner_id = inventory.get('owner')
        owner_profile_picture = ""

        if owner_id and ObjectId.is_valid(owner_id):
            owner = users_collection.find_one({'_id': ObjectId(owner_id)})
            if owner:
                owner_profile_picture = owner.get('profilePicture', "")

        # Update the inventory document with the new embedding and owner_profilePicture
        update_data = {
            'owner_profilePicture': owner_profile_picture,
            'embedding': embedding,
        }

        inventories_collection.update_one(
            {'_id': ObjectId(inventory_id)},
            {'$set': update_data}
        )

        return jsonify({'status': 'success', 'message': 'Inventory embedding and owner profile picture updated successfully'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/full_batch_embedding', methods=['POST'])
def add_embeddings_to_all_inventories():
    """
    Generate embeddings for all inventory items and update their MongoDB documents.
    """

    try:
        # Retrieve all inventory items from the database
        inventories = inventories_collection.find()

        updated_count = 0
        error_count = 0

        for inventory in inventories:
            try:
                # Combine relevant fields to create a text representation for embedding
                inventory_text = ' '.join(
                    str(value) for key, value in inventory.items() if key != '_id' and key != 'embedding'
                )

                # Generate the embedding
                embedding = generate_embedding(inventory_text)

                if embedding is not None:
                    # Update the inventory document with the new embedding
                    inventories_collection.update_one(
                        {'_id': inventory['_id']},
                        {'$set': {'embedding': embedding}}
                    )
                    updated_count += 1
                else:
                    error_count += 1

            except Exception as inner_exception:
                print(f"Error processing inventory with ID {inventory['_id']}: {str(inner_exception)}")
                error_count += 1

        return jsonify({
            'status': 'success',
            'message': f"Processed {updated_count + error_count} inventories.",
            'updated': updated_count,
            'errors': error_count
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(port=os.getenv("PORT", default=5000),debug=True)


