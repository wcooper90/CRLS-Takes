CREATE TABLE users (
  id  SERIAL PRIMARY KEY,
  dateJoined DATE,
  posts INTEGER DEFAULT 0,
  username VARCHAR NOT NULL,
  passwd VARCHAR NOT NULL
);
