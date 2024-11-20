from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import numpy as np, ast
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os
from pymongo import MongoClient
from supabase import create_client, Client
from utils import extract_text_from_image,SWAGGER_TEMPLATE,fetch_and_convert_image_to_base64
from bson import json_util
from flask_cors import CORS


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

# Add your existing endpoints below:
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')


def generate_embedding(text):
    try:
        return embedding_model.embed_query(text)
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

@app.route('/embed_inventories', methods=['POST'])
def embed_and_update_inventories():
    try:
        # Retrieve all documents in the inventories collection
        all_inventories = inventories_collection.find()
        
        for inventory in all_inventories:
            product_title = inventory['title']
            description = inventory['description']

            # try:
            #     cover_image  = inventory['images'][0] 
            #     cover_image_base64 = fetch_and_convert_image_to_base64(cover_image)
            #     # print(cover_image_base64)
            # except:
            #     print('imade download failed')
            
            embedding_vector = generate_embedding(f"{product_title}\n {description}")
            
            if embedding_vector is not None:
                # Update MongoDB document with embedding
                inventories_collection.update_one(
                    {'_id': inventory['_id']},  # Match the document by _id
                    {'$set': {'embedding': embedding_vector}}  # Set the embedding field
                )
        return jsonify({'status': 'success', 'message': 'Embeddings added to all inventories!'}), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500










@app.route('/search', methods=['POST'])
def search():
    try:
        # Get the search query from the request
        data = request.form
        query = data.get('query')
        
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
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)
        
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


if __name__ == '__main__':
    app.run(debug=True)
