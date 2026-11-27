
from connection import db

# MovieMatch collections
users = db["users"]
movies = db["movies"]
user_title_lists = db["user_title_lists"]
ratings = db["ratings"]

def show_collections():
    print("MovieMatch collections:")

    for collection in db.list_collection_names():
        print(f"- {collection}")

if __name__ == "__main__":
    # Create collections if they do not exist
    for name in ["users", "movies", "user_title_lists", "ratings"]:
        if name not in db.list_collection_names():
            db.create_collection(name)

    show_collections()
