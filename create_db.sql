DROP DATABASE IF EXISTS secrets;

DROP USER IF EXISTS secret_user;

CREATE DATABASE secrets WITH OWNER postgres;

CREATE USER secret_user WITH PASSWORD 'pass';

\connect secrets;

CREATE SCHEMA Secret;

CREATE TABLE Secret.Storage(
    SecretKey BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    Phrase VARCHAR(256) NOT NULL,
    SecretMessage BYTEA
);

CREATE OR REPLACE FUNCTION Secret.generate_secret(_phrase VARCHAR(256), _message BYTEA) RETURNS BIGINT AS
    $$
    BEGIN
        INSERT INTO Secret.Storage(Phrase, SecretMessage) VALUES (_phrase, _message);
        RETURN currval('Secret.Storage_SecretKey_seq');
    END;
    $$ LANGUAGE PLpgSQL;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA Secret TO secret_user;
GRANT USAGE ON SCHEMA Secret TO secret_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA Secret TO secret_user;
GRANT SELECT, INSERT, DELETE ON ALL TABLES IN SCHEMA Secret TO secret_user;
