CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  dateJoined DATE,
  posts INTEGER DEFAULT 0,
  username VARCHAR NOT NULL,
  passwd VARCHAR NOT NULL
);

CREATE TABLE takes (
  take VARCHAR NOT NULL,
  username VARCHAR NOT NULL,
  datePosted DATE
);


CREATE TABLE blogs (
  blog VARCHAR NOT NULL,
  id SERIAL PRIMARY KEY,
  username VARCHAR NOT NULL,
  datePosted DATE
);
