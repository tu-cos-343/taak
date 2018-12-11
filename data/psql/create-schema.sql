CREATE TABLE member (
  id         SERIAL      NOT NULL
    CONSTRAINT member_id_pk
      PRIMARY KEY,
  first_name VARCHAR(64) NOT NULL,
  last_name  VARCHAR(64) NOT NULL,
  email      VARCHAR(64) NOT NULL
);

CREATE TABLE posting (
  id          SERIAL    NOT NULL
    CONSTRAINT posting_id_pk
      PRIMARY KEY,
  title       TEXT      NOT NULL,
  content     TEXT      NOT NULL,
  when_posted TIMESTAMP NOT NULL
);

CREATE TABLE member_posting (
  member_id  INTEGER NOT NULL
    CONSTRAINT member_posting_member_id_fk
      REFERENCES member,
  posting_id INTEGER NOT NULL
    CONSTRAINT member_posting_posting_id_fk
      REFERENCES posting,
  CONSTRAINT member_posting_member_id_posting_id_pk
    PRIMARY KEY (member_id, posting_id)
);
