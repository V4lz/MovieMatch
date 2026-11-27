
from connection import db

# 1. USERS VALIDATOR
users_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "username", "email", "profile",
                     "favoriteGenres", "preferences", "createdAt"],
        "properties": {
            "_id": {"bsonType": "string"},
            "username": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "profile": {
                "bsonType": "object",
                "required": ["fullName", "bio", "profilePicture"],
                "properties": {
                    "fullName": {"bsonType": "string"},
                    "bio": {"bsonType": "string"},
                    "profilePicture": {"bsonType": "string"}
                }
            },
            "favoriteGenres": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "preferences": {
                "bsonType": "object",
                "required": ["language", "contentType",
                             "recommendationsEnabled"],
                "properties": {
                    "language": {"bsonType": "string"},
                    "contentType": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "recommendationsEnabled": {"bsonType": "bool"}
                }
            },
            "createdAt": {"bsonType": "date"}
        }
    }
}


# 2. MOVIES VALIDATOR
movies_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "title", "contentType", "description",
                     "genres", "releaseDate", "releaseYear", "createdAt"],
        "properties": {
            "_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "contentType": {
                "enum": ["Movie", "Series"]
            },
            "description": {"bsonType": "string"},
            "genres": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "releaseDate": {"bsonType": "date"},
            "releaseYear": {"bsonType": "int"},
            "duration": {"bsonType": ["int", "null"]},
            "director": {"bsonType": ["string", "null"]},
            "cast": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "language": {"bsonType": "string"},
            "createdAt": {"bsonType": "date"}
        }
    }
}


# 3. USER TITLE LISTS VALIDATOR
user_title_lists_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "userId", "movieId", "listType", "addedAt"],
        "properties": {
            "_id": {"bsonType": "string"},
            "userId": {"bsonType": "string"},
            "movieId": {"bsonType": "string"},
            "listType": {
                "enum": ["favorite", "watchlist"]
            },
            "addedAt": {"bsonType": "date"}
        }
    }
}


# 4. RATINGS VALIDATOR
ratings_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "userId", "movieId", "rating",
                     "createdAt", "updatedAt"],
        "properties": {
            "_id": {"bsonType": "string"},
            "userId": {"bsonType": "string"},
            "movieId": {"bsonType": "string"},
            "rating": {
                "bsonType": "int",
                "minimum": 1,
                "maximum": 5
            },
            "review": {"bsonType": "string"},
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"}
        }
    }
}


# Apply all validators
def apply_validators():
    validators = {
        "users": users_validator,
        "movies": movies_validator,
        "user_title_lists": user_title_lists_validator,
        "ratings": ratings_validator
    }

    for collection_name, validator in validators.items():
        db.command({
            "collMod": collection_name,
            "validator": validator,
            "validationLevel": "strict",
            "validationAction": "error"
        })

        print(f"Validator applied successfully: {collection_name}")


if __name__ == "__main__":
    apply_validators()
