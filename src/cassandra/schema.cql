CREATE KEYSPACE IF NOT EXISTS moviematch
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE moviematch;

CREATE TABLE IF NOT EXISTS activity_by_user_month (
    user_id text,
    activity_month text,
    event_time timestamp,
    event_id uuid,
    event_type text,
    movie_id text,
    previous_rating int,
    new_rating int,
    search_text text,
    recommendation_method text,
    PRIMARY KEY ((user_id, activity_month), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC);

CREATE TABLE IF NOT EXISTS activity_by_user_month_type (
    user_id text,
    activity_month text,
    event_type text,
    event_time timestamp,
    event_id uuid,
    movie_id text,
    previous_rating int,
    new_rating int,
    search_text text,
    recommendation_method text,
    PRIMARY KEY ((user_id, activity_month, event_type), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC);

CREATE TABLE IF NOT EXISTS activity_by_title_day_type (
    movie_id text,
    activity_day date,
    event_type text,
    event_time timestamp,
    event_id uuid,
    user_id text,
    previous_rating int,
    new_rating int,
    recommendation_method text,
    PRIMARY KEY ((movie_id, activity_day, event_type), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC);
