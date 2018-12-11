import pytest
import requests

from db_config import psql_db, mongo_db


@pytest.fixture
def psql_cursor():
    """Create a new Postgres cursor for use by a test."""
    with psql_db:
        with psql_db.cursor() as cursor:
            yield cursor
            psql_db.commit()


@pytest.fixture
def comment_collection():
    """Retrieve the comment collection for the Mongo instance."""
    return mongo_db['comments']


@pytest.fixture
def delete_sample_data(psql_cursor, comment_collection):
    """Delete all relevant data."""
    psql_cursor.execute('DELETE FROM member_posting')
    psql_cursor.execute('DELETE FROM member')
    psql_cursor.execute('DELETE FROM posting')
    comment_collection.drop()


@pytest.fixture
def create_sample_data(psql_cursor, comment_collection):
    """Seed Postgres and Mongo with sample data."""

    # Add members to Postgres; hang on to their (autogenerated) IDs.
    insert_member = """
        INSERT INTO member (first_name, last_name, email)
        VALUES (%(fname)s, %(lname)s, %(email)s)
        RETURNING id
    """
    member_ids = []
    for member in [{'fname': 'Fred', 'lname': 'Ziffle', 'email': 'fred@ziffle.com'},
                   {'fname': 'Zelda', 'lname': 'Ziffle', 'email': 'zelda@gmail.com'}]:
        psql_cursor.execute(insert_member, member)
        result = psql_cursor.fetchone()
        member_ids.append(result['id'])
    assert len(member_ids) == 2

    # Create a posting in Postgres.
    insert_posting = """
        INSERT INTO posting (title, content, when_posted)
        VALUES (%(title)s, %(content)s, %(when)s)
        RETURNING id
    """
    psql_cursor.execute(insert_posting, {
        'title': 'Info on the Ziffles',
        'content': 'The Ziffles have relocated to South America!',
        'when': '2018-12-07 23:11:13'})
    result = psql_cursor.fetchone()
    posting_id = result['id']
    assert posting_id is not None

    # Map a member to the posting
    insert_member_posting = """
        INSERT INTO member_posting (member_id, posting_id)
        VALUES (%(m_id)s, %(p_id)s)
    """
    psql_cursor.execute(insert_member_posting, {
        'm_id': member_ids[0],
        'p_id': posting_id
    })

    # Commit all the INSERT operations.
    psql_cursor.connection.commit()

    # Add a moderately elaborate set of comments for the posting to Mongo.
    comment_collection.insert_one({
        "posting_id": posting_id,
        "comments": [
            {
                "comments": [
                    {
                        "comments": [],
                        "content": "Good luck to them.",
                        "id": "5c0bf4b7fd54967b9af13a63"
                    }
                ],
                "content": "That's wonderful!",
                "id": "5c0be855fd54967195a9d467"
            },
            {
                "comments": [
                    {
                        "comments": [],
                        "content": "Just outside Lima, actually.",
                        "id": "5c0bf475fd54967b9af13a60"
                    },
                    {
                        "comments": [
                            {
                                "comments": [],
                                "content": "It really is lovely.",
                                "id": "5c0bf49cfd54967b9af13a62"
                            }
                        ],
                        "content": "What a nice spot.",
                        "id": "5c0bf484fd54967b9af13a61"
                    }
                ],
                "content": "Where in Peru, if you don't mind?",
                "id": "5c0be86afd54967195a9d469"
            }
        ]
    })


@pytest.mark.usefixtures('delete_sample_data')
def test_delete_sample_data(psql_cursor):
    """Check that we're clearing out the database"""
    psql_cursor.execute('SELECT * FROM member')
    results = psql_cursor.fetchall()
    assert len(results) == 0


@pytest.mark.usefixtures('delete_sample_data', 'create_sample_data')
def test_get_members():
    """Make sure we're adding members to the database."""
    resp = requests.get('http://localhost:5000/members')
    json = resp.json()
    assert resp.status_code == 200
    assert len(json) == 2
    assert json[0]['email'] == 'fred@ziffle.com'
    assert json[1]['email'] == 'zelda@gmail.com'


@pytest.mark.usefixtures('delete_sample_data', 'create_sample_data')
def test_get_postings(psql_cursor):
    """Make sure we're adding postings."""
    psql_cursor.execute('SELECT * FROM member_posting')
    resp = requests.get('http://localhost:5000/postings')
    assert len(resp.json()) == 1


if __name__ == '__main__':
    test_get_members()