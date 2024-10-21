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



SWAGGER_TEMPLATE = {
  "swagger": "2.0",
  "info": {
    "title": "Search API",
    "description": "API for searching products in the inventory.",
    "version": "1.0.0"
  },
  "host": "https://safelink-search-api.onrender.com",  
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
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "_id": {
                    "type": "object",
                    "properties": {
                      "$oid": {
                        "type": "string",
                        "example": "66faf5eab0d7086885949951"
                      }
                    }
                  },
                  "title": {
                    "type": "string",
                    "example": "Soft ponmo chops dipped in fried pepperstew"
                  },
                  "description": {
                    "type": "string",
                    "example": "This ponmo delicacy goes with any type of drinks and can be used for any type of events."
                  },
                  "price": {
                    "type": "number",
                    "example": 15000
                  },
                  "currency": {
                    "type": "string",
                    "example": "NGN"
                  },
                  "images": {
                    "type": "array",
                    "items": {
                      "type": "string",
                      "example": "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722981/o0enwomd3thy5x71gf6j.jpg"
                    }
                  },
                  "videos": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "owner": {
                    "type": "object",
                    "properties": {
                      "$oid": {
                        "type": "string",
                        "example": "66d4cc5d67cf6df5d674517c"
                      }
                    }
                  },
                  "__v": {
                    "type": "integer",
                    "example": 0
                  }
                }
              }
            },
            "examples": [
              {
                "_id": {"$oid": "66faf5eab0d7086885949951"},
                "title": "Soft ponmo chops dipped in fried pepperstew",
                "description": "This ponmo delicacy goes with any type of drinks and can be used for any type of events.",
                "price": 15000,
                "currency": "NGN",
                "images": [
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722981/o0enwomd3thy5x71gf6j.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722982/ps9sew3hck5uw0icpeuz.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722982/hngnm7thij4lwev2tryy.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722983/lo2bz2eishsq3as5l2r6.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722984/skci45nbuer3fle4qktc.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722984/amwyuk3avmmzdaguedn0.jpg",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722985/xwkeyt5kzb5kv50tibcl.jpg"
                ],
                "videos": [],
                "owner": {"$oid": "66d4cc5d67cf6df5d674517c"},
                "__v": 0
              },
              {
                "_id": {"$oid": "66fab5b7758fc2f694f38507"},
                "title": "My Product",
                "description": "Test",
                "price": 50,
                "currency": "USD",
                "images": [
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727706549/tkyi6kehrpbmfmhjrfax.png",
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1727706550/w4e18z3lkxbcjdkk03vv.jpg"
                ],
                "videos": [],
                "owner": {"$oid": "66d372ec6f8432cf6e26163f"},
                "__v": 0
              },
              {
                "_id": {"$oid": "66cbbf952fd88c69c63eb304"},
                "title": "clothes",
                "description": "clothes",
                "price": 7000,
                "currency": "NGN",
                "images": [
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1724628884/CREAM%20CARD%20RESOURCES/aeffm8hdkxebjjymi1wr.jpg"
                ],
                "videos": [],
                "owner": {"$oid": "66ca38fcb5c3e35a4ebe024c"},
                "__v": 0
              },
              {
                "_id": {"$oid": "66d4d03c67cf6df5d67451a6"},
                "title": "Brown bag",
                "description": "Very fine brown bag with camel leather",
                "price": 5000,
                "currency": "NGN",
                "images": [
                  "https://res.cloudinary.com/dtori4rq2/image/upload/v1725222970/CREAM%20CARD%20RESOURCES/unbw3to2k5wkgksx97uj.jpg"
                ],
                "videos": [],
                "owner": {"$oid": "66d4cc5d67cf6df5d674517c"},
                "__v": 0
              },
              {
                "_id": {"$oid": "65110ec05746557aead4bac6"},
                "title": "House",
                "description": "Dey Play My Fans",
                "price": 70000,
                "currency": "NGN",
                "images": [
                  "http://res.cloudinary.com/dtori4rq2/image/upload/v1695617077/CREAM%20CARD%20RESOURCES/ubksgczmq9ivsldmgyty.png",
                  "http://res.cloudinary.com/dtori4rq2/image/upload/v1695617083/CREAM%20CARD%20RESOURCES/f6smgrnblbspla7k4iph.png",
                  "http://res.cloudinary.com/dtori4rq2/image/upload/v1695617084/CREAM%20CARD%20RESOURCES/dvthckuwmswl7axginev.png",
                  "http://res.cloudinary.com/dtori4rq2/image/upload/v1695617089/CREAM%20CARD%20RESOURCES/sqeymvrzfsbuaju5brl8.png"
                ],
                "videos": [
                  "http://res.cloudinary.com/dtori4rq2/video/upload/v1695616701/CREAM%20CARD%20RESOURCES/vwge13z4i56zzieimesp.mp4"
                ],
                "owner": {"$oid": "65110cb178e2589a9914c094"},
                "__v": 1
              }
            ]
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
