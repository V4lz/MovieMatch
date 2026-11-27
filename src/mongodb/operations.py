
from datetime import datetime, timezone
from connection import db


# 1. Create a user
def create_user(user_data):
    return db.users.insert_one(user_data)


# 2. Update a user's profile
def update_user_profile(user_id, full_name, bio, profile_picture):
    return db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "profile.fullName": full_name,
                "profile.bio": bio,
                "profile.profilePicture": profile_picture
            }
        }
    )


# 3. Update favorite genres
def update_favorite_genres(user_id, genres):
    return db.users.update_one(
        {"_id": user_id},
        {"$set": {"favoriteGenres": genres}}
    )


# 4. Update user preferences
def update_preferences(user_id, language, content_types,
                       recommendations_enabled):
    return db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "preferences.language": language,
                "preferences.contentType": content_types,
                "preferences.recommendationsEnabled":
                    recommendations_enabled
            }
        }
    )


# 5. Add a movie to favorites or watchlist
def add_title_to_list(user_id, movie_id, list_type):
    if list_type not in ["favorite", "watchlist"]:
        raise ValueError("Invalid list type")

    list_id = f"{user_id}_{movie_id}_{list_type}"

    return db.user_title_lists.update_one(
        {
            "userId": user_id,
            "movieId": movie_id,
            "listType": list_type
        },
        {
            "$setOnInsert": {
                "_id": list_id,
                "userId": user_id,
                "movieId": movie_id,
                "listType": list_type,
                "addedAt": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )


# 6. Remove a movie from favorites or watchlist
def remove_title_from_list(user_id, movie_id, list_type):
    if list_type not in ["favorite", "watchlist"]:
        raise ValueError("Invalid list type")

    return db.user_title_lists.delete_one({
        "userId": user_id,
        "movieId": movie_id,
        "listType": list_type
    })


# 7. Create or update a rating
def save_rating(user_id, movie_id, rating, review=None):
    if not isinstance(rating, int) or isinstance(rating, bool):
        raise ValueError("Rating must be an integer")

    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5")

    now = datetime.now(timezone.utc)

    fields = {
        "rating": rating,
        "updatedAt": now
    }

    if review is not None:
        fields["review"] = review

    return db.ratings.update_one(
        {
            "userId": user_id,
            "movieId": movie_id
        },
        {
            "$set": fields,
            "$setOnInsert": {
                "_id": f"rating_{user_id}_{movie_id}",
                "userId": user_id,
                "movieId": movie_id,
                "createdAt": now
            }
        },
        upsert=True
    )


# 8. Update an existing written review
def update_review(user_id, movie_id, review):
    return db.ratings.update_one(
        {
            "userId": user_id,
            "movieId": movie_id
        },
        {
            "$set": {
                "review": review,
                "updatedAt": datetime.now(timezone.utc)
            }
        }
    )


# Run operation tests
if __name__ == "__main__":

    print("\n--- Update user profile ---")
    result = update_user_profile(
        "user_001",
        "Movie Fan Updated",
        "I enjoy science fiction movies.",
        "profile_001.jpg"
    )
    print("Modified:", result.modified_count)

    print("\n--- Update favorite genres ---")
    result = update_favorite_genres(
        "user_001",
        ["Sci-Fi", "Adventure", "Drama"]
    )
    print("Modified:", result.modified_count)

    print("\n--- Update preferences ---")
    result = update_preferences(
        "user_001",
        "English",
        ["Movie", "Series"],
        True
    )
    print("Modified:", result.modified_count)

    print("\n--- Add movie to favorites ---")
    result = add_title_to_list(
        "user_001", "movie_001", "favorite"
    )
    print("Matched:", result.matched_count)
    print("Inserted:", result.upserted_id)

    print("\n--- Add movie to watchlist ---")
    result = add_title_to_list(
        "user_001", "movie_001", "watchlist"
    )
    print("Matched:", result.matched_count)
    print("Inserted:", result.upserted_id)

    print("\n--- Save rating and review ---")
    result = save_rating(
        "user_001",
        "movie_001",
        5,
        "An amazing movie with a creative story."
    )
    print("Matched:", result.matched_count)
    print("Inserted:", result.upserted_id)

    print("\n--- Update written review ---")
    result = update_review(
        "user_001",
        "movie_001",
        "An excellent movie with a very creative story."
    )
    print("Modified:", result.modified_count)

    print("\nAll operation tests completed!")
