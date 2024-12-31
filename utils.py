import base64
import os

import requests
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymongo import MongoClient
from bson.objectid import ObjectId



load_dotenv()


client = MongoClient(os.getenv("MONGODB_URL"))

# Connect to the cream-card database
db = client['cream-card']

chat = ChatOpenAI(model="gpt-4o-mini")
# Fetch everything from the inventories collection
inventories_collection = db['inventories']
users_collection = db['users']


# Retrieve all documents in the inventories collection
all_inventories = inventories_collection.find()




def fetch_and_convert_image_to_base64(cloudinary_url):
    try:
        # Fetch the image from Cloudinary
        response = requests.get(cloudinary_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the image content (binary data)
            image_content = response.content
            
            # Convert binary data to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            return image_base64
        else:
            print(f"Failed to fetch the image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching or converting the image: {str(e)}")
        return None


def extract_text_from_image(base64_img):
    """Function to extract the content of the uploaded image"""

    try:
        msg = chat.invoke([
            AIMessage(content="You are an expert at identifying objects in an image and giving very accurate descriptions."),
            HumanMessage(content=[
                {"type": "text", "text": "Summarize the characteristics of the image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}",
                        "detail": "low",
                    },
                },
            ])
        ])

        return msg.content
    except Exception as e:
        print(f"Error extracting text from image: {str(e)}")
        return ""


# Add your existing endpoints below:
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')


def generate_embedding(text):
    try:
        return embedding_model.embed_query(text)
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None
    

def update_all_inventories():
    """
    Update all inventories with embeddings and owner profile pictures.
    """
    try:
        # Retrieve all documents in the inventories collection
        all_inventories = inventories_collection.find()

        for inventory in all_inventories:
            # Combine relevant fields to create a text representation for embedding
            inventory_text = ' '.join(
                str(value) for key, value in inventory.items() if key in ['title', 'description', 'price', 'currency']
            )

            # Generate the embedding
            embedding_vector = generate_embedding(inventory_text)

            if embedding_vector is None:
                print(f"Error generating embedding for inventory ID: {inventory['_id']}")
                continue

            # Retrieve the owner's profile picture
            owner_id = inventory.get('owner')
            owner_profile_picture = ""

            if owner_id and ObjectId.is_valid(owner_id):
                owner = users_collection.find_one({'_id': ObjectId(owner_id)})
                if owner:
                    owner_profile_picture = owner.get('profilePicture', "")

            # Update MongoDB document with embedding and owner_profilePicture
            inventories_collection.update_one(
                {'_id': inventory['_id']},  # Match the document by _id
                {
                    '$set': {
                        'embedding': embedding_vector,
                        'owner_profilePicture': owner_profile_picture
                    }
                }
            )

        return {'status': 'success', 'message': 'Embeddings and owner profile pictures added to all inventories!'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'status': 'error', 'message': str(e)}



if __name__ == "__main__":
    print(extract_text_from_image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"))
