from langchain.schema import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

chat = ChatOpenAI(model="gpt-4o-mini")


import requests
import base64

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
    "title": "Search API",
    "description": "API for searching products in the inventory.",
    "version": "1.0.0"
  },
  "host": "localhost:5000",  
  "basePath": "/",
  "schemes": [
    "http"
  ],
  "paths": {
    "/search": {
      "post": {
        "summary": "Search for products",
        "description": "Returns a list of products matching the search query.",
        "parameters": [
          {
            "name": "query",
            "in": "formData",
            "required": True,
            "type": "string",
            "description": "The search term to look for in the inventory."
          }
        ],
        "responses": {
          "200": {
            "description": "A successful response",
            "schema": {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "example": "success"
                },
                "results": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "_id": {
                        "type": "string",
                        "example": "64b8f2de9c8b1f0012a4abf3"
                      },
                      "title": {
                        "type": "string",
                        "example": "Product A"
                      },
                      "description": {
                        "type": "string",
                        "example": "Description of Product A"
                      },
                      "price": {
                        "type": "number",
                        "example": 25.99
                      },
                      "stock": {
                        "type": "integer",
                        "example": 10
                      }
                    }
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid input",
            "schema": {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "example": "error"
                },
                "message": {
                  "type": "string",
                  "example": "No query provided"
                }
              }
            }
          },
          "500": {
            "description": "Internal server error",
            "schema": {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "example": "error"
                },
                "message": {
                  "type": "string",
                  "example": "Error generating embedding"
                }
              }
            }
          }
        }
      }
    }
  }
}




if __name__ == "__main__":
    print(extract_text_from_image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"))
