import datetime

from bson import ObjectId
from bson.json_util import dumps
from flask import Flask, request, Response
from flask.json import jsonify

from db_config import mongo_db, psql_db

comment_collection = mongo_db['comments']

# Flask server
api = Flask(__name__)


@api.route('/members')
def get_all_members():
    cursor = psql_db.cursor()
    cursor.execute('SELECT * FROM member')
    members = cursor.fetchall()
    # return jsonify(members)
    return Response(dumps(members), mimetype='application/json')


@api.route('/members/<int:member_id>/postings')
def get_member_postings(member_id):
    """Get the postings for a particular member."""

    query = """
        SELECT posting.id, when_posted, title, content
        FROM posting
        INNER JOIN member_posting ON posting.id = member_posting.posting_id
        INNER JOIN member ON member_posting.member_id = member.id
        WHERE member.id = %(id)s;
    """
    cursor = psql_db.cursor()
    cursor.execute(query, {'id': member_id})
    postings = cursor.fetchall()
    return jsonify(postings)


@api.route('/postings', methods=['POST'])
def create_post():
    insert_posting = """
    INSERT INTO posting(title, content, when_posted)
    VALUES (%(title)s, %(content)s, %(when_posted)s)
    RETURNING *
    """
    insert_association = """
               INSERT INTO member_posting(member_id, posting_id)
               VALUES(%(m_id)s, %(p_id)s)
               """
    with psql_db:
        with psql_db.cursor() as cursor:
            cursor.execute(insert_posting, {
                'title': request.json['title'],
                'content': request.json['content'],
                'when_posted': request.json['when_posted'] or datetime.datetime.now()
            })
            result = cursor.fetchone()
            posting_id = result['id']

            cursor.execute(insert_association, {
                'm_id': request.json['member_id'],
                'p_id': posting_id
            })
    return 'ok'


def resolve_comments(posting):
    comments = comment_collection.find_one({'posting_id': posting['id']}, {'_id': 0})
    posting['comments'] = comments['comments'] if comments else []


@api.route('/postings')
def get_all_postings():
    cursor = psql_db.cursor()
    cursor.execute('SELECT * FROM posting')
    postings = cursor.fetchall()
    return jsonify(postings)


@api.route('/postings/<int:posting_id>')
def get_one_posting(posting_id):
    """Get the posting with the given ID."""
    cursor = psql_db.cursor()
    cursor.execute('SELECT * FROM posting WHERE id=%(p_id)s', {'p_id': posting_id})
    posting = cursor.fetchone()
    if posting is None:
        return "No such posting", 404
    resolve_comments(posting)
    return jsonify(posting)


def new_comment(content):
    """Construct a new comment with a unique ID and the given `content`."""
    return {
        "id": str(ObjectId()),
        "content": content,
        "comments": []
    }


def add_comment_helper(comments, comment_id, content):
    for comment in comments:
        if comment['id'] == comment_id:
            comment['comments'].append(new_comment(content))
            return True
        else:
            if add_comment_helper(comment['comments'], comment_id, content):
                return True
    return False


@api.route('/postings/<int:posting_id>', methods=['POST'])
@api.route('/postings/<int:posting_id>/<string:comment_id>', methods=['POST'])
def add_comment(posting_id, comment_id=None):
    """Add a comment to a posting."""
    with psql_db:
        with psql_db.cursor() as cursor:
            cursor.execute('SELECT * FROM posting WHERE id=%(p_id)s', {'p_id': posting_id})
            posting = cursor.fetchone()
            if posting is None:
                return "Posting {} doesn't exist".format(posting_id), 404

    comment_doc = comment_collection.find_one({'posting_id': posting_id})
    if comment_doc is None:
        comment_collection.insert_one({
            "posting_id": posting['id'],
            "comments": [new_comment(request.json['content'])]
        })
    elif comment_id is None:
        comment_collection.update_one({'posting_id': posting_id},
                                      {'$push': {'comments': new_comment(request.json['content'])}})
    else:
        if not add_comment_helper(comment_doc['comments'], comment_id, request.json['content']):
            return 'No comment with id {}'.format(comment_id), 404
        comment_collection.update_one({'posting_id': posting_id},
                                      {'$set': {'comments': comment_doc['comments']}})
    return 'ok'


@api.route('/comments')
def get_all_comments():
    all_comments = []
    for comment in comment_collection.find():
        all_comments.append(comment)
    return Response(dumps(all_comments), mimetype='application/json')
