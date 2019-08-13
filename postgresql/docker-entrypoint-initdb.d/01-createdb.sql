CREATE USER getitfixed;
CREATE DATABASE getitfixed OWNER getitfixed;
CREATE DATABASE getitfixed_tests OWNER getitfixed;
\connect getitfixed;
CREATE EXTENSION postgis;
\connect getitfixed_tests;
CREATE EXTENSION postgis;
