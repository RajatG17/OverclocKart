-- Create users and grant access
CREATE USER authuser WITH PASSWORD 'authpw';
CREATE USER cataloguser WITH PASSWORD 'catalogpw';
CREATE USER orderuser WITH PASSWORD 'orderpw';

-- Create DBs
CREATE DATABASE authdb OWNER authuser;
CREATE DATABASE catalogdb OWNER cataloguser;
CREATE DATABASE orderdb OWNER orderuser;

GRANT ALL PRIVILEGES ON DATABASE authdb TO authuser;
GRANT ALL PRIVILEGES ON DATABASE catalogdb TO cataloguser;
GRANT ALL PRIVILEGES ON DATABASE orderdb TO orderuser;

GRANT CONNECT ON DATABASE authdb TO authuser;
GRANT CONNECT ON DATABASE catalogdb TO cataloguser;
GRANT CONNECT ON DATABASE orderdb TO orderuser;