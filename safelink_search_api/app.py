from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Initialize the OpenAI embedding model and ChromaDB vector store
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Initialize ChromaDB (you can set persist_directory to None for in-memory)
persist_directory = "db"  # Change this if you want a persistent database
vector_store = Chroma(embedding_function=embedding_model, persist_directory=persist_directory)

# Endpoint to create an embedding from text
@app.route('/create_embedding', methods=['POST'])
def create_embedding():
    data = request.json
    embedding_id = data.get('id')
    text = data.get('text')

    # Check if the embedding with this ID already exists
    if embedding_id in vector_store.get_ids():
        return jsonify({"error": "Embedding with this ID already exists."}), 400

    try:
        # Generate embedding and add to Chroma
        embedding_vector = embedding_model.embed_query(text)
        vector_store.add_texts([text], metadatas=[{"id": embedding_id}], ids=[embedding_id])

        return jsonify({"message": "Embedding created successfully", "id": embedding_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to generate embedding: {str(e)}"}), 500


# Endpoint to search for embeddings
@app.route('/search', methods=['POST'])
def search_embedding():
    data = request.json
    query_text = data.get('text')

    try:
        # Generate embedding vector for query text
        query_vector = embedding_model.embed_query(query_text)

        # Perform similarity search with ChromaDB
        search_results = vector_store.similarity_search(query_text, k=5)  # Search for top 5 most similar results
        results = [{"id": result.metadata['id'], "score": result.score} for result in search_results]

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to search embeddings: {str(e)}"}), 500


# Endpoint to update an embedding
@app.route('/update_embedding/<embedding_id>', methods=['PUT'])
def update_embedding(embedding_id):
    try:
        data = request.json
        new_text = data.get('text')

        # Remove the existing embedding first if it exists
        vector_store.delete(ids=[embedding_id])

        # Generate new embedding and add it to ChromaDB
        new_embedding_vector = embedding_model.embed_query(new_text)
        vector_store.add_texts([new_text], metadatas=[{"id": embedding_id}], ids=[embedding_id])

        return jsonify({"message": "Embedding updated successfully", "id": embedding_id}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update embedding: {str(e)}"}), 500


# Endpoint to delete an embedding
@app.route('/delete_embedding/<embedding_id>', methods=['DELETE'])
def delete_embedding(embedding_id):
    try:
        # Remove embedding from ChromaDB
        vector_store.delete(ids=[embedding_id])

        return jsonify({"message": "Embedding deleted successfully", "id": embedding_id}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete embedding: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
