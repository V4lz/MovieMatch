import argparse
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from dotenv import load_dotenv

TABLES = ("activity_by_user_month", "activity_by_user_month_type", "activity_by_title_day_type")
GROUPS = {
    "ratings": ("rating_added", "rating_updated", "rating_deleted"),
    "searches": ("search_submitted",),
    "views": ("title_viewed",),
    "watchlist": ("watchlist_added", "watchlist_removed"),
    "favorites": ("favorite_added", "favorite_removed"),
    "clicks": ("recommendation_clicked",),
}
EVENT_TYPES = {event_type for group in GROUPS.values() for event_type in group}


@dataclass(frozen=True)
class Event:
    user_id: str
    event_type: str
    event_id: UUID
    event_time: datetime
    movie_id: str | None = None
    previous_rating: int | None = None
    new_rating: int | None = None
    search_text: str | None = None
    recommendation_method: str | None = None

    @classmethod
    def create(cls, user_id, event_type, **fields):
        return cls(user_id, event_type, uuid4(), datetime.now(timezone.utc), **fields)


def connect():
    load_dotenv()
    hosts = os.getenv("CASSANDRA_HOSTS", "localhost").split(",")
    return Cluster([host.strip() for host in hosts], port=int(os.getenv("CASSANDRA_PORT", "9042")))


class ActivityStore:
    def __init__(self, session):
        self.session = session
        payload = "event_time, event_id, movie_id, previous_rating, new_rating, search_text, recommendation_method"
        columns = (
            f"user_id, activity_month, event_type, {payload}",
            f"user_id, activity_month, event_type, {payload}",
            "movie_id, activity_day, event_type, event_time, event_id, user_id, "
            "previous_rating, new_rating, recommendation_method",
        )
        filters = (
            "user_id = ? AND activity_month = ?",
            "user_id = ? AND activity_month = ? AND event_type = ?",
            "movie_id = ? AND activity_day = ? AND event_type = ?",
        )
        self.inserts = []
        self.selects = []
        for table, fields, criteria in zip(TABLES, columns, filters):
            placeholders = ", ".join("?" for _ in fields.split(", "))
            self.inserts.append(session.prepare(f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"))
            self.selects.append(session.prepare(f"SELECT * FROM {table} WHERE {criteria}"))

    def record(self, event):
        if event.event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event.event_type}")
        if event.event_time.utcoffset() is None:
            raise ValueError("Event timestamp must include a timezone")
        if event.event_type == "search_submitted":
            if not event.search_text or event.movie_id is not None:
                raise ValueError("Search events require search_text and no movie_id")
        elif not event.movie_id:
            raise ValueError("This event requires movie_id")

        time = event.event_time.astimezone(timezone.utc)
        user_row = (
            event.user_id, time.strftime("%Y-%m"), event.event_type,
            time, event.event_id, event.movie_id, event.previous_rating,
            event.new_rating, event.search_text, event.recommendation_method,
        )
        # A logged batch delivers every projection of this one event.
        batch = BatchStatement()
        batch.add(self.inserts[0], user_row)
        batch.add(self.inserts[1], user_row)
        if event.movie_id:
            batch.add(self.inserts[2], (
                event.movie_id, time.date(), event.event_type, time, event.event_id,
                event.user_id, event.previous_rating, event.new_rating, event.recommendation_method,
            ))
        self.session.execute(batch)

    def monthly(self, user_id, month):
        return self.rows(0, (user_id, month))

    def by_type(self, user_id, month, event_type):
        return self.rows(1, (user_id, month, event_type))

    def category(self, user_id, month, category):
        rows = [
            row for event_type in GROUPS[category] for row in self.by_type(user_id, month, event_type)
        ]
        rows.sort(key=lambda row: row["event_id"])
        rows.sort(key=lambda row: row["event_time"], reverse=True)
        return rows

    def title_activity(self, movie_id, day, event_type):
        return self.rows(2, (movie_id, date.fromisoformat(day), event_type))

    def rows(self, query_index, parameters):
        return [row._asdict() for row in self.session.execute(self.selects[query_index], parameters)]


def setup(session, keyspace):
    if not keyspace.isascii() or not keyspace.isidentifier() or keyspace.lower() != keyspace:
        raise ValueError("Use a lowercase Cassandra keyspace identifier")
    schema = Path(__file__).with_name("schema.cql").read_text(encoding="utf-8")
    for statement in schema.replace("moviematch", keyspace).split(";"):
        if statement.strip():
            session.execute(statement.strip())


def seed(store):
    time = datetime(2026, 11, 7, 16, 30, tzinfo=timezone.utc)
    samples = [
        ("user_001", "search_submitted", {"search_text": "space travel"}),
        ("user_001", "title_viewed", {"movie_id": "movie_001"}),
        ("user_001", "rating_added", {"movie_id": "movie_001", "new_rating": 3}),
        ("user_001", "rating_updated", {"movie_id": "movie_001", "previous_rating": 3, "new_rating": 5}),
        ("user_002", "rating_updated", {"movie_id": "movie_001", "previous_rating": 4, "new_rating": 5}),
        ("user_001", "watchlist_added", {"movie_id": "movie_002"}),
        ("user_001", "watchlist_removed", {"movie_id": "movie_002"}),
        ("user_001", "favorite_added", {"movie_id": "movie_001"}),
        ("user_001", "favorite_removed", {"movie_id": "movie_001"}),
        ("user_001", "recommendation_clicked", {"movie_id": "movie_003", "recommendation_method": "collaborative"}),
        ("user_001", "search_submitted", {"search_text": "science fiction"}),
        ("user_001", "rating_deleted", {"movie_id": "movie_004", "previous_rating": 4}),
        ("user_003", "rating_updated", {"movie_id": "movie_001", "previous_rating": 3, "new_rating": 4}),
    ]
    for minute, (user_id, event_type, fields) in enumerate(samples):
        event_id = UUID(f"a2d7bafe-5bf3-4d74-9e64-{minute:012x}")
        store.record(Event(user_id, event_type, event_id, time + timedelta(minutes=minute), **fields))


def demo(store):
    monthly = store.monthly("user_001", "2026-11")
    groups = {name: store.category("user_001", "2026-11", name) for name in GROUPS}
    title = store.title_activity("movie_001", "2026-11-07", "rating_updated")
    assert len(monthly) == 11
    assert [row["event_time"] for row in monthly] == sorted(
        (row["event_time"] for row in monthly), reverse=True
    )
    assert [len(rows) for rows in groups.values()] == [3, 2, 1, 2, 2, 1]
    assert len(title) == 3
    assert str(groups["clicks"][0]["recommendation_method"]) == "collaborative"
    event_id = next(row["event_id"] for row in title if row["user_id"] == "user_001")
    assert any(row["event_id"] == event_id for row in monthly)
    assert any(row["event_id"] == event_id for row in groups["ratings"])
    return dict(monthly=monthly, **groups, title_activity=title)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["setup", "seed", "demo", "monthly", "category", "title"])
    parser.add_argument("--user", default="user_001")
    parser.add_argument("--month", default="2026-11")
    parser.add_argument("--day", default="2026-11-07")
    parser.add_argument("--movie", default="movie_001")
    parser.add_argument("--event", choices=sorted(EVENT_TYPES), default="rating_updated")
    parser.add_argument("--category", choices=GROUPS, default="ratings")
    args = parser.parse_args()
    with connect() as cluster:
        keyspace = os.getenv("CASSANDRA_KEYSPACE", "moviematch")
        if args.action == "setup":
            setup(cluster.connect(), keyspace)
            print("setup OK")
            return

        store = ActivityStore(cluster.connect(keyspace))
        actions = {
            "seed": lambda: seed(store),
            "demo": lambda: demo(store),
            "monthly": lambda: store.monthly(args.user, args.month),
            "category": lambda: store.category(args.user, args.month, args.category),
            "title": lambda: store.title_activity(args.movie, args.day, args.event),
        }
        result = actions[args.action]()
        print(json.dumps(result, indent=2, default=str) if result is not None else "seed OK")


if __name__ == "__main__":
    main()
