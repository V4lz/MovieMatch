import argparse
import json
import os
from pathlib import Path

import pydgraph
from dotenv import load_dotenv

DIRECTORY = Path(__file__).resolve().parent


def fragment(name):
    return (DIRECTORY / f"{name}.dql").read_text(encoding="utf-8")


class MovieGraph:
    def __init__(self):
        load_dotenv()
        host = os.getenv("DGRAPH_HOST", "localhost")
        port = os.getenv("DGRAPH_GRPC_PORT", "9080")
        self.stub = pydgraph.DgraphClientStub(f"{host}:{port}")
        self.client = pydgraph.DgraphClient(self.stub)

    def close(self):
        self.stub.close()

    def setup(self):
        self.client.alter(pydgraph.Operation(schema=fragment("schema")))

    def query(self, query, variables):
        txn = self.client.txn(read_only=True)
        try:
            return json.loads(txn.query(query, variables=variables).json)
        finally:
            txn.discard()

    def similar_users(self, user_id):
        query = "query similar($user: string) {\n"
        query += fragment("similarity") + fragment("similar_users") + "}"
        return self.query(query, {"$user": user_id}).get("similar_users", [])

    def recommend(self, user_id, genre=None):
        variables = {"$user": user_id}
        signature = "$user: string"
        genre_block = ""
        genre_filter = ""
        if genre is not None:
            signature += ", $genre: string"
            variables["$genre"] = genre
            genre_block = """
  var(func: eq(genre_name, $genre)) {
    inGenre as ~has_genre
  }
"""
            genre_filter = " @filter(uid(inGenre))"

        query = f"query recommend({signature}) {{\n"
        query += "var(func: eq(user_id, $user)) { alreadyRated as rated }\n"
        query += fragment("similarity") + fragment("candidates") + genre_block
        query += f"recommendations(func: uid(votes), orderdesc: val(votes)){genre_filter} {{\n"
        query += fragment("recommendations") + "}"
        return self.query(query, variables).get("recommendations", [])

    def related(self, movie_id):
        return self.query(fragment("related"), {"$movie": movie_id}).get("related_titles", [])

    def following(self, user_id):
        accounts = self.query(fragment("following"), {"$user": user_id}).get("following", [])
        return [account for account in accounts if account.get("titles")]

    def reverse(self, user_id, genre):
        return self.query(fragment("reverse"), {"$user": user_id, "$genre": genre})

    def upsert_node(self, node_type, key, value, **fields):
        # The predicate comes from the MovieGraph methods. Values are JSON-escaped.
        query = f"{{ node as var(func: eq({key}, {json.dumps(value, ensure_ascii=False)})) }}"
        mutation = pydgraph.Mutation(set_json=json.dumps({
            "uid": "uid(node)", "dgraph.type": [node_type], key: value, **fields,
        }).encode())
        txn = self.client.txn()
        try:
            txn.do_request(txn.create_request(
                query=query, mutations=[mutation], commit_now=True
            ))
        finally:
            txn.discard()

    def uid(self, predicate, value):
        query = f"query lookup($value: string) {{ nodes(func: eq({predicate}, $value)) {{ uid }} }}"
        nodes = self.query(query, {"$value": value}).get("nodes", [])
        if len(nodes) != 1:
            raise ValueError(f"Expected one node for {predicate}={value}, got {len(nodes)}")
        return nodes[0]["uid"]

    def save_user(self, user_id):
        self.upsert_node("User", "user_id", user_id)

    def save_title(self, movie_id, title, genres):
        for genre in dict.fromkeys(genres):
            self.upsert_node("Genre", "genre_name", genre)
        links = [{"uid": self.uid("genre_name", genre)} for genre in dict.fromkeys(genres)]
        self.upsert_node("Title", "movie_id", movie_id, title_name=title)
        uid = self.uid("movie_id", movie_id)
        txn = self.client.txn()
        try:
            txn.mutate(
                del_nquads=f"<{uid}> <has_genre> * .",
                set_obj={"uid": uid, "has_genre": links},
                commit_now=True,
            )
        finally:
            txn.discard()

    def save_rating(self, user_id, movie_id, score):
        if type(score) is not int or not 1 <= score <= 5:
            raise ValueError("Score must be an integer from 1 to 5")
        self.write_edge(
            self.uid("user_id", user_id), "rated",
            {"uid": self.uid("movie_id", movie_id), "rated|score": score},
        )

    def delete_rating(self, user_id, movie_id):
        user = self.uid("user_id", user_id)
        title = self.uid("movie_id", movie_id)
        txn = self.client.txn()
        try:
            txn.mutate(del_nquads=f"<{user}> <rated> <{title}> .", commit_now=True)
        finally:
            txn.discard()

    def follow(self, user_id, followed_id):
        self.write_edge(
            self.uid("user_id", user_id), "follows",
            {"uid": self.uid("user_id", followed_id)},
        )

    def write_edge(self, source, predicate, target):
        txn = self.client.txn()
        try:
            txn.mutate(set_obj={"uid": source, predicate: [target]}, commit_now=True)
        finally:
            txn.discard()


def seed(graph):
    # IDs, titles and genres follow src/mongodb/add_catalog.py.
    titles = [
        ("movie_001", "Inception", ["Sci-Fi", "Action", "Thriller"]),
        ("movie_002", "Interstellar", ["Sci-Fi", "Drama", "Adventure"]),
        ("movie_003", "The Matrix", ["Sci-Fi", "Action"]),
        ("movie_004", "The Shawshank Redemption", ["Drama"]),
        ("movie_005", "The Dark Knight", ["Action", "Crime", "Drama"]),
    ]
    ratings = {
        "user_001": [(1, 5), (2, 4), (5, 2)],
        "user_002": [(1, 5), (2, 5), (3, 5), (4, 4), (5, 5)],
        "user_003": [(1, 4), (2, 4), (3, 4), (4, 3)],
        "user_004": [(1, 5), (2, 3), (4, 5)],
    }
    for movie_id, title, genres in titles:
        graph.save_title(movie_id, title, genres)
    for user_id, scores in ratings.items():
        graph.save_user(user_id)
        for number, score in scores:
            graph.save_rating(user_id, f"movie_{number:03}", score)
    graph.follow("user_001", "user_002")
    graph.follow("user_001", "user_004")
    graph.follow("user_003", "user_002")


def demo(graph):
    user = "user_001"
    similar = graph.similar_users(user)
    recommendations = graph.recommend(user)
    drama = graph.recommend(user, "Drama")
    related = graph.related("movie_001")
    following = graph.following(user)
    reverse = graph.reverse("user_002", "Sci-Fi")
    assert {item["user_id"]: item["shared_count"] for item in similar} == {
        "user_002": 2, "user_003": 2,
    }
    assert [(item["movie_id"], item["similar_user_count"]) for item in recommendations] == [
        ("movie_003", 2), ("movie_004", 1),
    ]
    assert {item["user_id"] for item in recommendations[0]["recommended_by"]} == {
        "user_002", "user_003",
    }
    assert all(len(item["shared_titles"]) == 2 for item in recommendations[0]["recommended_by"])
    assert [item["movie_id"] for item in drama] == ["movie_004"]
    assert any(item["movie_id"] == "movie_002" for item in related)
    assert {title["movie_id"] for account in following for title in account["titles"]} == {
        "movie_003", "movie_004",
    }
    assert {item["user_id"] for item in reverse["accounts"][0]["followers"]} == {
        "user_001", "user_003",
    }
    assert {item["movie_id"] for item in reverse["genres"][0]["titles"]} == {
        "movie_001", "movie_002", "movie_003",
    }
    return dict(similar=similar, recommendations=recommendations, drama=drama,
                related=related, following=following, reverse=reverse)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["setup", "seed", "demo", "similar", "recommend",
                                           "related", "following", "reverse"])
    parser.add_argument("--user", default="user_001")
    parser.add_argument("--movie", default="movie_001")
    parser.add_argument("--genre")
    args = parser.parse_args()
    graph = MovieGraph()
    try:
        actions = {
            "setup": graph.setup,
            "seed": lambda: seed(graph),
            "demo": lambda: demo(graph),
            "similar": lambda: graph.similar_users(args.user),
            "recommend": lambda: graph.recommend(args.user, args.genre),
            "related": lambda: graph.related(args.movie),
            "following": lambda: graph.following(args.user),
            "reverse": lambda: graph.reverse(args.user, args.genre or "Sci-Fi"),
        }
        result = actions[args.action]()
        print(json.dumps(result, indent=2) if result is not None else f"{args.action} OK")
    finally:
        graph.close()


if __name__ == "__main__":
    main()
