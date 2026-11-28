
from datetime import datetime, timezone
from connection import db

now = datetime.now(timezone.utc)

catalog = [
    {
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
    },
    {
        "_id": "movie_002",
        "title": "Interstellar",
        "contentType": "Movie",
        "description": "A group of explorers travels through a wormhole to find a new home for humanity.",
        "genres": ["Sci-Fi", "Drama", "Adventure"],
        "releaseDate": datetime(2014, 11, 7, tzinfo=timezone.utc),
        "releaseYear": 2014,
        "duration": 169,
        "director": "Christopher Nolan",
        "cast": ["Matthew McConaughey", "Anne Hathaway"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_003",
        "title": "The Matrix",
        "contentType": "Movie",
        "description": "A computer hacker discovers that reality is a simulation controlled by machines.",
        "genres": ["Sci-Fi", "Action"],
        "releaseDate": datetime(1999, 3, 31, tzinfo=timezone.utc),
        "releaseYear": 1999,
        "duration": 136,
        "director": "Lana Wachowski, Lilly Wachowski",
        "cast": ["Keanu Reeves", "Laurence Fishburne"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_004",
        "title": "The Shawshank Redemption",
        "contentType": "Movie",
        "description": "A banker sentenced to life in prison forms a friendship and holds on to hope.",
        "genres": ["Drama"],
        "releaseDate": datetime(1994, 9, 23, tzinfo=timezone.utc),
        "releaseYear": 1994,
        "duration": 142,
        "director": "Frank Darabont",
        "cast": ["Tim Robbins", "Morgan Freeman"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_005",
        "title": "The Dark Knight",
        "contentType": "Movie",
        "description": "Batman faces the Joker, a criminal who brings chaos to Gotham City.",
        "genres": ["Action", "Crime", "Drama"],
        "releaseDate": datetime(2008, 7, 18, tzinfo=timezone.utc),
        "releaseYear": 2008,
        "duration": 152,
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Heath Ledger"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_006",
        "title": "Titanic",
        "contentType": "Movie",
        "description": "Two young passengers from different social classes fall in love aboard the Titanic.",
        "genres": ["Romance", "Drama"],
        "releaseDate": datetime(1997, 12, 19, tzinfo=timezone.utc),
        "releaseYear": 1997,
        "duration": 194,
        "director": "James Cameron",
        "cast": ["Leonardo DiCaprio", "Kate Winslet"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_007",
        "title": "Jurassic Park",
        "contentType": "Movie",
        "description": "A theme park with cloned dinosaurs becomes dangerous when its security systems fail.",
        "genres": ["Adventure", "Sci-Fi", "Thriller"],
        "releaseDate": datetime(1993, 6, 11, tzinfo=timezone.utc),
        "releaseYear": 1993,
        "duration": 127,
        "director": "Steven Spielberg",
        "cast": ["Sam Neill", "Laura Dern"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_008",
        "title": "Coco",
        "contentType": "Movie",
        "description": "A young boy travels to the Land of the Dead to discover his family's history through music.",
        "genres": ["Animation", "Family", "Fantasy"],
        "releaseDate": datetime(2017, 11, 22, tzinfo=timezone.utc),
        "releaseYear": 2017,
        "duration": 105,
        "director": "Lee Unkrich",
        "cast": ["Anthony Gonzalez", "Gael García Bernal"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_009",
        "title": "Parasite",
        "contentType": "Movie",
        "description": "A poor family gradually becomes involved in the lives of a wealthy household.",
        "genres": ["Thriller", "Drama"],
        "releaseDate": datetime(2019, 5, 30, tzinfo=timezone.utc),
        "releaseYear": 2019,
        "duration": 132,
        "director": "Bong Joon-ho",
        "cast": ["Song Kang-ho", "Lee Sun-kyun"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "movie_010",
        "title": "The Truman Show",
        "contentType": "Movie",
        "description": "A man discovers that his entire life is being broadcast as a television show.",
        "genres": ["Comedy", "Drama", "Sci-Fi"],
        "releaseDate": datetime(1998, 6, 5, tzinfo=timezone.utc),
        "releaseYear": 1998,
        "duration": 103,
        "director": "Peter Weir",
        "cast": ["Jim Carrey", "Laura Linney"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "series_001",
        "title": "Breaking Bad",
        "contentType": "Series",
        "description": "A chemistry teacher turns to producing illegal drugs after being diagnosed with cancer.",
        "genres": ["Crime", "Drama", "Thriller"],
        "releaseDate": datetime(2008, 1, 20, tzinfo=timezone.utc),
        "releaseYear": 2008,
        "duration": 47,
        "director": "Vince Gilligan",
        "cast": ["Bryan Cranston", "Aaron Paul"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "series_002",
        "title": "Stranger Things",
        "contentType": "Series",
        "description": "A group of friends encounters supernatural forces and secret experiments in their town.",
        "genres": ["Sci-Fi", "Horror", "Drama"],
        "releaseDate": datetime(2016, 7, 15, tzinfo=timezone.utc),
        "releaseYear": 2016,
        "duration": 50,
        "director": "The Duffer Brothers",
        "cast": ["Millie Bobby Brown", "Finn Wolfhard"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "series_003",
        "title": "Dark",
        "contentType": "Series",
        "description": "The disappearance of children reveals a complex mystery involving time travel and four families.",
        "genres": ["Sci-Fi", "Mystery", "Thriller"],
        "releaseDate": datetime(2017, 12, 1, tzinfo=timezone.utc),
        "releaseYear": 2017,
        "duration": 60,
        "director": "Baran bo Odar",
        "cast": ["Louis Hofmann", "Lisa Vicari"],
        "language": "German",
        "createdAt": now
    },
    {
        "_id": "series_004",
        "title": "The Office",
        "contentType": "Series",
        "description": "The daily lives of office employees are documented in a mockumentary-style comedy.",
        "genres": ["Comedy"],
        "releaseDate": datetime(2005, 3, 24, tzinfo=timezone.utc),
        "releaseYear": 2005,
        "duration": 22,
        "director": "Greg Daniels",
        "cast": ["Steve Carell", "John Krasinski"],
        "language": "English",
        "createdAt": now
    },
    {
        "_id": "series_005",
        "title": "Wednesday",
        "contentType": "Series",
        "description": "Wednesday Addams investigates mysterious events at Nevermore Academy.",
        "genres": ["Mystery", "Comedy", "Fantasy"],
        "releaseDate": datetime(2022, 11, 23, tzinfo=timezone.utc),
        "releaseYear": 2022,
        "duration": 45,
        "director": "Tim Burton",
        "cast": ["Jenna Ortega", "Emma Myers"],
        "language": "English",
        "createdAt": now
    }
]

# Insert or update titles without creating duplicates
for title in catalog:
    db.movies.replace_one(
        {"_id": title["_id"]},
        title,
        upsert=True
    )

print("MovieMatch catalog inserted successfully!")
print(f"Total titles: {db.movies.count_documents({})}")
print(f"Movies: {db.movies.count_documents({'contentType': 'Movie'})}")
print(f"Series: {db.movies.count_documents({'contentType': 'Series'})}")

print("\nCatalog:")
for title in db.movies.find({}, {"_id": 1, "title": 1, "contentType": 1}):
    print(f"{title['_id']} - {title['title']} ({title['contentType']})")
