













SWAGGER_TEMPLATE = {
  "swagger": "2.0",
  "info": {
    "title": "Safelink Search API",
    "description": "API for searching products in the inventory.",
    "version": "1.0.0"
  },
  "host": "https://safelink.up.railway.app",  
  "basePath": "/",
  "schemes": [
    "http"
  ],
  "paths": {
      "/add_inventory_to_ai": {
            "post": {
                "operationId": "add_inventory_to_ai",
                "summary": "Generate embedding for an inventory item",
                "description": "This endpoint generates an embedding for a specific inventory item based on its ID and updates the database.",
                "parameters": [
                    {
                        "name": "inventory_id",
                        "in": "formData",
                        "required": True,
                        "description": "JSON object containing the inventory_id of the item to process.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "inventory_id": {
                                    "type": "string",
                                    "description": "The ObjectId of the inventory item."
                                }
                            },
                            "required": ["inventory_id"]
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Embedding successfully generated and updated.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request or missing data.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    },
                    "404": {
                        "description": "Inventory item not found.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    },
                    "500": {
                        "description": "Internal server error.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
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
                "owner_profilePicture": {
                  "type": "string",
                  "example": "https://res.cloudinary.com/dtori4rq2/image/upload/v1732050362/v3cmpzf32riit49zgqbb.jpg"
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
              "_id": { "$oid": "66faf5eab0d7086885949951" },
              "title": "Soft ponmo chops dipped in fried pepperstew",
              "description": "This ponmo delicacy goes with any type of drinks and can be used for any type of events.",
              "price": 15000,
              "currency": "NGN",
              "images": [
                "https://res.cloudinary.com/dtori4rq2/image/upload/v1727722981/o0enwomd3thy5x71gf6j.jpg"
              ],
              "videos": [],
              "owner": { "$oid": "66d4cc5d67cf6df5d674517c" },
              "owner_profilePicture": "https://res.cloudinary.com/dtori4rq2/image/upload/v1732050362/v3cmpzf32riit49zgqbb.jpg",
              "__v": 0
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



