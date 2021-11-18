CREATE TABLE users (
    user_id text NOT NULL,
    hashcode text primary key NOT NULL,
    passw text NOT NULL,
    last_post_id int,
    FOREIGN KEY(last_post_id) REFERENCES posts(post_id)
);

CREATE TABLE posts (
    post_id int primary key NOT NULL,
    post_timestamp text NOT NULL,
    poster_user_id text NOT NULL,
    post_title text NOT NULL,
    post_content text NOT NULL,
    vote_counter int NOT NULL,
    FOREIGN KEY(poster_user_id) REFERENCES users(user_id)
);


CREATE TRIGGER aft_del AFTER DELETE ON users
BEGIN
    DELETE FROM posts
        WHERE poster_user_id=OLD.user_id;
END;