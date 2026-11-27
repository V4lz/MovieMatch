
from datetime import datetime, timezone
from connection import db
from operations import (
    create_user,
    add_title_to_list,
    remove_title_from_list,
    save_rating
)

# Use a separate test user to protect the original sample data
test_user_id = "user_test_002"

# Remove previous test data so the script can be executed again
db.users.delete_one({"_id": test_user_id})
db.user_title_lists.delete_many({"userId": test_user_id})

# 1. Test creating a new user
print("\n--- Create a new user ---")

test_user = {
    "_id": test_user_id,
    "username": "test_user",
    "email": "test_user@example.com",
    "profile": {
        "fullName": "Test User",
        "bio": "Testing MovieMatch.",
        "profilePicture": "test.jpg"
    },
    "favoriteGenres": ["Sci-Fi"],
    "preferences": {
        "language": "English",
        "contentType": ["Movie"],
        "recommendationsEnabled": True
    },
    "createdAt": datetime.now(timezone.utc)
}

result = create_user(test_user)
print("User created:", result.inserted_id)


# 2. Test adding a movie to favorites
print("\n--- Add movie to favorites ---")

add_title_to_list(test_user_id, "movie_001", "favorite")
print("Favorite added:", db.user_title_lists.count_documents({
    "userId": test_user_id,
    "listType": "favorite"
}))


# 3. Test removing a movie from favorites
print("\n--- Remove movie from favorites ---")

result = remove_title_from_list(
    test_user_id, "movie_001", "favorite"
)
print("Favorites removed:", result.deleted_count)


# 4. Test adding a movie to watchlist
print("\n--- Add movie to watchlist ---")

add_title_to_list(test_user_id, "movie_001", "watchlist")
print("Watchlist added:", db.user_title_lists.count_documents({
    "userId": test_user_id,
    "listType": "watchlist"
}))


# 5. Test removing a movie from watchlist
print("\n--- Remove movie from watchlist ---")

result = remove_title_from_list(
    test_user_id, "movie_001", "watchlist"
)
print("Watchlist removed:", result.deleted_count)


# 6. Test rating validation
print("\n--- Test invalid rating ---")

try:
    save_rating(test_user_id, "movie_001", 6, "Invalid rating")
    print("ERROR: Invalid rating was accepted.")
except ValueError as error:
    print("Invalid rating rejected:", error)


print("\nAll additional tests completed!")
