
from datetime import datetime, timezone
from connection import db

# Fecha actual
now = datetime.now(timezone.utc)

# 1. Usuario de prueba
user = {
    "_id": "user_001",
    "username": "movie_fan",
    "email": "moviefan@example.com",
    "profile": {
        "fullName": "Movie Fan",
        "bio": "I love watching movies and series.",
        "profilePicture": "profile_001.jpg"
    },
    "favoriteGenres": ["Sci-Fi", "Action", "Adventure"],
    "preferences": {
        "language": "English",
        "contentType": ["Movie", "Series"],
        "recommendationsEnabled": True
    },
    "createdAt": now
}

# 2. Película de prueba
movie = {
    "_id": "movie_001",
    "title": "Inception",
    "contentType": "Movie",
    "description": "A thief enters people's dreams to steal information.",
    "genres": ["Sci-Fi", "Action", "Thriller"],
    "releaseDate": datetime(2010, 7, 16, tzinfo=timezone.utc),
    "releaseYear": 2010,
    "duration": 148,
    "director": "Christopher Nolan",
    "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
    "language": "English",
    "createdAt": now
}

# 3. Registros de listas
title_lists = [
    {
        "_id": "list_001",
        "userId": "user_001",
        "movieId": "movie_001",
        "listType": "favorite",
        "addedAt": now
    },
    {
        "_id": "list_002",
        "userId": "user_001",
        "movieId": "movie_001",
        "listType": "watchlist",
        "addedAt": now
    }
]

# 4. Calificación y reseña
rating = {
    "_id": "review_001",
    "userId": "user_001",
    "movieId": "movie_001",
    "rating": 5,
    "review": "An amazing movie with a creative story.",
    "createdAt": now,
    "updatedAt": now
}

# Insertar o actualizar datos sin duplicarlos
db.users.replace_one({"_id": user["_id"]}, user, upsert=True)
db.movies.replace_one({"_id": movie["_id"]}, movie, upsert=True)

for item in title_lists:
    db.user_title_lists.replace_one(
        {"_id": item["_id"]}, item, upsert=True
    )

db.ratings.replace_one(
    {"_id": rating["_id"]}, rating, upsert=True
)

print("Sample data inserted successfully!")

print(f"Users: {db.users.count_documents({})}")
print(f"Movies: {db.movies.count_documents({})}")
print(f"User title lists: {db.user_title_lists.count_documents({})}")
print(f"Ratings: {db.ratings.count_documents({})}")
