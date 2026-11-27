
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE")

# Create MongoDB client
client = MongoClient(MONGODB_URI)

# Select database
db = client[DATABASE_NAME]


def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB Atlas connection successful!")
        print(f"Connected database: {DATABASE_NAME}")
    except Exception as error:
        print(f"MongoDB connection failed: {error}")


if __name__ == "__main__":
    test_connection()
