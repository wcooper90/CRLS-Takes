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
  datePosted DATE,
  bName VARCHAR NOT NULL
  typeB VARCHAR NOT NULL
);

Stuff to connect to adminer --
Host
    ec2-54-235-134-25.compute-1.amazonaws.com
Database
    d3gbkv3egf6krp
User
    cnfjlelhbsbqdj
Port
    5432
Password
    43a55fcedde5bbb4f27c30a1a384f18f76600704afaf42ef9d6f07dce82d0b9c
