from langchain.schema import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

chat = ChatOpenAI(model="gpt-4o-mini")


def extract_text_from_image(base64_img):
    """Function to extract the content of the uploaded image"""

    try:
        msg = chat.invoke([
            AIMessage(content="You are an expert at identifying objects in an image and giving very accurate descriptions."),
            HumanMessage(content=[
                {"type": "text", "text": "Briefly tell me what is in  the image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_img,
                        "detail": "low",
                    },
                },
            ])
        ])

        return msg.content
    except Exception as e:
        print(f"Error extracting text from image: {str(e)}")
        return ""



SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "SafeLink Search API",
        "description": "API for creating, searching, updating, and deleting embeddings for performing advanced keyword search",
        "version": "1.0.0"
    },
    "host": "localhost:5000",  # Change this to your host
    "basePath": "/",
    "schemes": ["http"],
    "paths": {
        "/search": {
            "post": {
                "summary": "Search embeddings",
                "description": "THIS IS THE ACTUAL SEARCH FUNCITONALITY ... (Searches for products by embedding similarity for a given user_id)",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "query_text": {"type": "string"}
                            },
                            "example": {
                                "query_text": "Sample search query"
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Search results returned"},
                    "400": {"description": "No input text or user_id provided"},
                    "404": {"description": "No embeddings found for the given user_id"}
                }
            }
        },
        "/create_embedding": {
            "post": {
                "summary": "Create an embedding",
                "description": "Creates an embedding from text and saves it to the database",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "user_id": {"type": "string"},
                                "product_title": {"type": "string"},
                                "base64_img": {"type": "string"}
                            },
                            "example": {
                                "product_id": "12345",
                                "user_id": "67890",
                                "product_title": "Sample Product",
                                "base64_img": "data:image/png;base64,..."
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "Embedding created successfully"},
                    "500": {"description": "Failed to generate embedding"}
                }
            }
        },
        
        "/update_embedding": {
            "put": {
                "summary": "Update an embedding",
                "description": "Updates an existing embedding in the database",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "user_id": {"type": "string"},
                                "product_title": {"type": "string"},
                                "base64_img": {"type": "string"}
                            },
                            "example": {
                                "product_id": "12345",
                                "user_id": "67890",
                                "product_title": "Updated Product",
                                "base64_img": "data:image/png;base64,..."
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Embedding updated successfully"},
                    "500": {"description": "Failed to update embedding"}
                }
            }
        },
        "/delete_embedding": {
            "delete": {
                "summary": "Delete an embedding",
                "description": "Deletes an embedding using user_id and product_id",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "user_id": {"type": "string"}
                            },
                            "example": {
                                "product_id": "12345",
                                "user_id": "67890"
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Embedding deleted successfully"},
                    "500": {"description": "Failed to delete embedding"}
                }
            }
        }
    }
}



if __name__ == "__main__":
    print(extract_text_from_image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"))
