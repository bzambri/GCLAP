-- creating database
CREATE DATABASE single_levels;
CREATE DATABASE zonal_means;

-- creating users
CREATE USER brian WITH PASSWORD '<your-password>';

-- granting permissions
GRANT ALL ON DATABASE single_levels TO brian;
GRANT ALL ON DATABASE zonal_means TO brian;
