DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS date_range;

CREATE TABLE requests (
    date            INTEGER,
    loaded          INTEGER,
    doubles         INTEGER,
    for_creation    INTEGER,
    for_expand      INTEGER,
    handle_over     INTEGER,
    returned        INTEGER,
    sent_for_handle INTEGER,
    packages        INTEGER
);

CREATE TABLE users (
    date     INTEGER,
    user_fio TEXT    
);

CREATE TABLE date_range (
    min_date INTEGER,
    max_date INTEGER    
);

