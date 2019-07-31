getitfixed README
==================

Getting Started
---------------

- cd <directory containing this file>

- sudo su postgres

- psql -c "CREATE USER \"www-data\" WITH PASSWORD 'www-data';"

- export DATABASE=getitfixed
- psql -d postgres -c "CREATE DATABASE $DATABASE OWNER \"www-data\";"
- psql -d $DATABASE -c "CREATE EXTENSION postgis;"

Manually update sqlalchemy.url in development.ini

- make initdb
- make serve
