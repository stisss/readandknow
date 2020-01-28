DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS saved;
DROP TABLE IF EXISTS followers;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  last_name TEXT,
  createdwhy TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  institution TEXT,
  password TEXT NOT NULL
);

CREATE TABLE article (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  description TEXT,
  body TEXT NOT NULL,
  magazine TEXT,
  reactions INTEGER DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE comment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE saved (
  id_user INTEGER,
  id_article INTEGER,
  FOREIGN KEY (id_user) REFERENCES user (id),
  FOREIGN KEY (id_article) REFERENCES article (id),
  PRIMARY KEY (id_user, id_article)
);


CREATE TABLE followers (
  id_follower INTEGER,
  id_followed INTEGER,
  FOREIGN KEY (id_follower) REFERENCES user (id),
  FOREIGN KEY (id_followed) REFERENCES user (id),
  PRIMARY KEY (id_follower, id_followed)
);
