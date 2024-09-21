from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import numpy as np, ast
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os
from supabase import create_client, Client
from utils import extract_text_from_image,SWAGGER_TEMPLATE


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)

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


# Endpoint to create an embedding from text
@app.route('/create_embedding', methods=['POST'])
def create_embedding():
    data = request.json
    product_id = data.get('product_id')
    user_id = data.get("user_id")
    product_title = data.get('product_title')
    base64_img = data.get('base64_img')
    generated_description = extract_text_from_image(base64_img)

    embedding_vector = generate_embedding(f"{product_title}: {generated_description}")

    if embedding_vector is None:
        return jsonify({"error": "Failed to generate embedding"}), 500

    response = (
        supabase.table("products")
        .insert({
            "user_id": user_id,
            "product_id": product_id,
            'product_title': product_title,
            'embedding': embedding_vector
        })
        .execute()
    )

    return jsonify({"message": "Embedding created successfully"}), 201


@app.route('/search', methods=['POST'])
def search_embedding():
    data = request.json
    query_text = data.get('query_text')
    user_id = data.get('user_id')  # Get user_id from the request

    if not query_text:
        return jsonify({"error": "No input text provided"}), 400  # Return 400 for bad request

    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400  # Ensure user_id is provided

    query_vector = generate_embedding(query_text)
    if query_vector is None:
        return jsonify({"error": "Failed to generate embedding for query"}), 500

    try:
        response = (
            supabase.table('products')
            .select('product_id, product_title, embedding')
            .eq('user_id', user_id)  # Filter by user_id
            .execute()
        )

        if response.data is None or len(response.data) == 0:
            return jsonify({"error": "No embeddings found for the given user_id"}), 404  # Return 404 if no data

        similarities = []

        for record in response.data:
            product_id = record['product_id']
            product_title = record['product_title']
            stored_embedding = np.array(ast.literal_eval(record['embedding']))  # Convert string to numpy array

            similarity = cosine_similarity([query_vector], [stored_embedding])[0][0]

            similarities.append({
                "user_id":user_id,
                "product_id": product_id,
                "title": product_title,
                "similarity": similarity
            })

        sorted_similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)

        return jsonify({"results": sorted_similarities}), 200

    except Exception as e:
        print(f"Error retrieving embeddings: {str(e)}")
        return jsonify({"error": "Failed to retrieve embeddings"}), 500


@app.route('/update_embedding', methods=['PUT'])
def update_embedding():
    data = request.json
    product_id = data.get('product_id')
    user_id = data.get("user_id")
    product_title = data.get('product_title')
    base64_img = data.get('base64_img')
    generated_description = extract_text_from_image(base64_img)
    new_embedding_vector = generate_embedding(f"{product_title}: {generated_description}")

    if new_embedding_vector is None:
        return jsonify({"error": "Failed to generate embedding"}), 500

    try:
        response = (
            supabase.table('products')
            .update({'embedding': new_embedding_vector})
            .eq('user_id', user_id)
            .eq('product_id', int(product_id))
            .execute()
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to update embedding"}), 500

        return jsonify({"message": "Embedding updated successfully", "product_id": int(product_id)}), 200

    except Exception as e:
        print(f"Error updating embedding: {str(e)}")
        return jsonify({"error": "Failed to update embedding"}), 500


@app.route('/delete_embedding', methods=['DELETE'])
def delete_embedding():
    data = request.json
    product_id = data.get('product_id')
    user_id = data.get("user_id")

    try:
        response = (
            supabase.table('products')
            .delete()
            .eq('user_id', user_id)
            .eq('product_id', int(product_id))
            .execute()
        )

        return jsonify({"message": "Embedding deleted successfully", "product_id": product_id}), 200

    except Exception as e:
        print(f"Error deleting embedding: {str(e)}")
        return jsonify({"error": "Failed to delete embedding"}), 500


if __name__ == '__main__':
    app.run(debug=True)
