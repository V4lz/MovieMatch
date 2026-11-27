
from connection import db


# 1. Retrieve a user's watchlist
def get_watchlist_aggregation(user_id):
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
                "title": "$movie.title",
                "genres": "$movie.genres",
                "contentType": "$movie.contentType",
                "addedAt": 1
            }
        },
        {"$sort": {"addedAt": -1}}
    ]))


# 2. Calculate average rating and total ratings per movie
def get_movie_rating_statistics():
    return list(db.ratings.aggregate([
        {
            "$group": {
                "_id": "$movieId",
                "averageRating": {"$avg": "$rating"},
                "totalRatings": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "movies",
                "localField": "_id",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "movieId": "$_id",
                "title": "$movie.title",
                "averageRating": 1,
                "totalRatings": 1
            }
        },
        {"$sort": {"averageRating": -1}},
        {"$limit": 10}
    ]))


# 3. Find highest-rated movies within a genre
def get_highest_rated_by_genre(genre):
    return list(db.movies.aggregate([
        {
            "$match": {
                "genres": {
                    "$regex": f"^{genre}$",
                    "$options": "i"
                }
            }
        },
        {
            "$lookup": {
                "from": "ratings",
                "let": {"movie_id": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$movieId", "$$movie_id"]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "averageRating": {"$avg": "$rating"},
                            "totalRatings": {"$sum": 1}
                        }
                    }
                ],
                "as": "ratingStats"
            }
        },
        {
            "$unwind": {
                "path": "$ratingStats",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "genres": 1,
                "averageRating": {
                    "$ifNull": ["$ratingStats.averageRating", 0]
                },
                "totalRatings": {
                    "$ifNull": ["$ratingStats.totalRatings", 0]
                }
            }
        },
        {"$sort": {"averageRating": -1}},
        {"$limit": 10}
    ]))


# 4. Get the highest-rated movies and series
def get_top_rated_titles():
    return list(db.ratings.aggregate([
        {
            "$group": {
                "_id": "$movieId",
                "averageRating": {"$avg": "$rating"},
                "totalRatings": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "movies",
                "localField": "_id",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "movieId": "$_id",
                "title": "$movie.title",
                "contentType": "$movie.contentType",
                "averageRating": 1,
                "totalRatings": 1
            }
        },
        {"$sort": {
            "averageRating": -1,
            "totalRatings": -1
        }},
        {"$limit": 10}
    ]))



# Run aggregation tests
if __name__ == "__main__":

    print("\n--- User watchlist aggregation ---")
    for result in get_watchlist_aggregation("user_001"):
        print(result)

    print("\n--- Movie rating statistics ---")
    for result in get_movie_rating_statistics():
        print(result)

    print("\n--- Highest-rated Sci-Fi movies ---")
    for result in get_highest_rated_by_genre("Sci-Fi"):
        print(result)

    
    print("\n--- Top rated movies and series ---")
    for result in get_top_rated_titles():
        print(result)

