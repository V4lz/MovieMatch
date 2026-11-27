
from connection import db


def create_indexes():

    # USERS: 2 indexes
    db.users.create_index(
        [("email", 1)],
        unique=True
    )

    db.users.create_index(
        [("username", 1)],
        unique=True
    )

    # MOVIES: 3 indexes
    db.movies.create_index(
        [("title", "text")]
    )

    db.movies.create_index(
        [("genres", 1), ("releaseDate", -1)]
    )

    db.movies.create_index(
        [("contentType", 1)]
    )

    # USER TITLE LISTS: 2 indexes
    db.user_title_lists.create_index(
        [("userId", 1), ("movieId", 1), ("listType", 1)],
        unique=True
    )

    db.user_title_lists.create_index(
        [("userId", 1), ("listType", 1), ("addedAt", -1)]
    )

    # RATINGS: 2 indexes
    db.ratings.create_index(
        [("userId", 1), ("movieId", 1)],
        unique=True
    )

    db.ratings.create_index(
        [("movieId", 1), ("rating", -1)]
    )

    print("All 9 MongoDB indexes created successfully!")


if __name__ == "__main__":
    create_indexes()

    print("\nIndexes by collection:")

    for collection_name in db.list_collection_names():
        print(f"\n{collection_name}:")
        for index in db[collection_name].list_indexes():
            print(f"- {index['name']}")
