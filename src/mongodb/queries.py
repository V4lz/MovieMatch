
from connection import db


# 1. Search a movie by title
def search_movie_by_title(title):
    return list(db.movies.find({
        "title": {"$regex": title, "$options": "i"}
    }))


# 2. Filter movies by genre
def filter_movies_by_genre(genre):
    return list(db.movies.find({
        "genres": {"$regex": f"^{genre}$", "$options": "i"}
    }))


# 3. Get a user's watchlist
def get_watchlist(user_id):
    return list(db.user_title_lists.aggregate([
        {
            "$match": {
                "userId": user_id,
                "listType": "watchlist"
            }
        },
        {
            "$lookup": {
                "from": "movies",
                "localField": "movieId",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "movieId": 1,
                "title": "$movie.title",
                "genres": "$movie.genres",
                "contentType": "$movie.contentType",
                "addedAt": 1
            }
        }
    ]))


# 4. Get a user's favorite movies
def get_favorites(user_id):
    return list(db.user_title_lists.aggregate([
        {
            "$match": {
                "userId": user_id,
                "listType": "favorite"
            }
        },
        {
            "$lookup": {
                "from": "movies",
                "localField": "movieId",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "movieId": 1,
                "title": "$movie.title",
                "genres": "$movie.genres"
            }
        }
    ]))


# 5. Get a user's ratings
def get_user_ratings(user_id):
    return list(db.ratings.find(
        {"userId": user_id},
        {"_id": 0, "movieId": 1, "rating": 1, "review": 1}
    ))


# 6. Filter movies and series by content type
def filter_by_content_type(content_type):
    if content_type not in ["Movie", "Series"]:
        raise ValueError("Content type must be Movie or Series")

    return list(db.movies.find({
        "contentType": content_type
    }))


# 7. Filter by genre and content type
def filter_by_genre_and_type(genre, content_type):
    if content_type not in ["Movie", "Series"]:
        raise ValueError("Content type must be Movie or Series")

    return list(db.movies.find({
        "genres": {"$regex": f"^{genre}$", "$options": "i"},
        "contentType": content_type
    }))



# Run test queries
if __name__ == "__main__":
    print("\n--- Movie search ---")
    for movie in search_movie_by_title("Inception"):
        print(movie)

    print("\n--- Movies by genre ---")
    for movie in filter_movies_by_genre("Sci-Fi"):
        print(movie)

    print("\n--- User watchlist ---")
    for movie in get_watchlist("user_001"):
        print(movie)

    print("\n--- User favorites ---")
    for movie in get_favorites("user_001"):
        print(movie)

    print("\n--- User ratings ---")
    for rating in get_user_ratings("user_001"):
        print(rating)

    
    print("\n--- Movies only ---")
    for movie in filter_by_content_type("Movie"):
        print(movie["title"])

    print("\n--- Series only ---")
    for series in filter_by_content_type("Series"):
        print(series["title"])

    print("\n--- Sci-Fi movies ---")
    for movie in filter_by_genre_and_type("Sci-Fi", "Movie"):
        print(movie["title"])
