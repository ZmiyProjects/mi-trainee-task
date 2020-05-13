CREATE SCHEMA Secret;

CREATE TABLE Secret.Storage(
    StorageId BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    Phrase VARCHAR(256) NOT NULL,
    SecretMessage BYTEA NOT NULL,
    SecretKey VARCHAR(256) NULL,
    DeleteDate timestamp NULL
);

CREATE OR REPLACE FUNCTION Secret.generate_secret(_phrase VARCHAR(256), _message BYTEA, _del_date interval) RETURNS BIGINT AS
    $$
    BEGIN
        INSERT INTO Secret.Storage(Phrase, SecretMessage, DeleteDate) VALUES (_phrase, _message, CURRENT_TIMESTAMP + _del_date);
        RETURN currval('Secret.Storage_StorageId_seq');
    END;
    $$ LANGUAGE PLpgSQL;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA Secret TO secret_db_user;
GRANT USAGE ON SCHEMA Secret TO secret_db_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA Secret TO secret_db_user;
GRANT SELECT, INSERT, DELETE, UPDATE ON ALL TABLES IN SCHEMA Secret TO secret_db_user;
