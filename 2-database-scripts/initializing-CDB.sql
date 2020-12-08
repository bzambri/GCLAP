-- creating database
CREATE DATABASE era5;

-- creating users
CREATE USER brian WITH PASSWORD '<your-password>';

-- granting permissions
GRANT ALL ON DATABASE era5 TO brian;
