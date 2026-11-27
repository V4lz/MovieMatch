
from datetime import datetime, timezone
from connection import db

series = {
    "_id": "series_001",
    "title": "Breaking Bad",
    "contentType": "Series",
    "description": "A chemistry teacher turns to manufacturing drugs.",
    "genres": ["Crime", "Drama", "Thriller"],
    "releaseDate": datetime(2008, 1, 20, tzinfo=timezone.utc),
    "releaseYear": 2008,
    "duration": None,
    "director": None,
    "cast": ["Bryan Cranston", "Aaron Paul"],
    "language": "English",
    "createdAt": datetime.now(timezone.utc)
}

db.movies.replace_one(
    {"_id": series["_id"]},
    series,
    upsert=True
)

print("Series inserted successfully!")
print(db.movies.find_one({"_id": "series_001"}))
