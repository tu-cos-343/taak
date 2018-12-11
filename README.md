# COS 343 Final Exam Code

This code implements a simple RESTful API for a prototype blogging application.

## Relational Database

A Postgres database stores these tables:

1. `member` stores information about a "member" of the application web site.
    A member has a first name, last name, and email address,
    as well as a synthetic primary key (`id`).
1. `posting` stores a member post
    A posting has a title and content, and a synthetic primary key (`id`).
1. `member_posting` is an associative table that ties members to postings;
   it has foreign keys to both `member` and `posting`.
   Members can have mutiple posts and a post can have more than one member.
   
## Document Database

Members can post hierarchical comments on each posting.
Comments are stored in MongoDB
in a `comment` collection 
and are structured as illustrated 
in this example:
```json
{
  "posting_id": 17,
  "comments": [ 
    {
      "id": "5c0be855fd54967195a9d467",
      "content": "That's wonderful!",
      "comments": [
        {
          "id": "5c0bf4b7fd54967b9af13a63",
          "content": "Good luck to them.",
          "comments": []
        }
      ]
    },
    {
      "id": "5c0be86afd54967195a9d469",
      "content": "Where in Peru, if you don't mind?",
      "comments": [
        {
          "id": "5c0bf475fd54967b9af13a60",
          "content": "Just outside Lima, actually.",
          "comments": []
        },
        {
          "id": "5c0bf484fd54967b9af13a61",
          "content": "What a nice spot.",
          "comments": [
            {
              "id": "5c0bf49cfd54967b9af13a62",
              "content": "It really is lovely.",
              "comments": []
            }
          ]
        }
      ]
    }
  ]
}
```
At the top level, the `posting_id` connects these comments to a particular
posting in the RDBMS by its `id`.
Each `comments` list contains zero or more comments.
Each such comment contains:
- An `id`, which makes it easy to refer to a specific comment in the hierarchy
- The `content` of the comment
- A nested list of `comments` that allow comments on _this_ comment
  and so on _ad infinitum_.

## API Endpoints

The API defines the following endpoints:

### Members

1. `GET /members` returns all members
1. `GET /members/<member-id>/postings` returns all postings by a given member

### Postings

1. `GET /postings` returns all postings
1. `GET /postings/<posting-id>` returns a specific posting
1. `POST /postings` adds a new posting; 
   the payload includes:
- The `member_id` of the posting member
- The `title`, `content`, and time stamp for the post
   
### Comments

1. `GET /comments` returns all comments
1. `POST /postings/<posting-id>` adds a new _top-level_ comment to a post
1. `POST /postings/<posting-id>/<comment-id>` adds a new, non-top-level comment to an existing
   comment on the given post that has the indicated comment ID.

## Running the Server

You are encouraged to set up the API server and try it out.
That said, note that because this is sample code for an exam,
the code is not certified to be particularly robust.

### Installation

Use **Python 3**. Python 2 is going the way of the dodo.

I recommend that you set up a Python virtual environment
to avoid polluting your global Python installation.
To create and activate it:
```bash
$ python3 -m venv venv
$ source ./venv/bin/activate
```

Install the required Python packages.
With your virtual environment activated:
```bash
$ pip3 install -r requirements.txt
```

### Configuration

You will need to configure both Postgres and MongoDB.
If you don't have one or both of these set up on your own devices,
I suggest that you use `faraday.cse.taylor.edu` for Postgres
and `mlab.com` for MongoDB.
The `db-config.py` file includes all the configuration details
and a suggested format for a `bash` script 
that will supply enviornnment variables to make it all work.

Once you have connected to Postgres, 
load and execute the file `data/psql/create-schema.sql`
to create the necessary relational schema.
You don't need to initialize anything in Mongo.

## Running the tests

The `test_api.py` file contains some `pytest`-based tests
that exercise a few parts of the API.
After getting the server running, I'd suggest you run
these as a simple smoke test that you are set up properly.

To run the smoke tests, activate your virtualenvironment
and run:
```bash
$ pytest
```

## Kicking the tires

A good way to familiarize yourself with the interaction
between the API, Postgres, and Mongo
will be to issue requests to the API.

Suggested ways to issue requests:

1. [Postman](https://www.getpostman.com/) -- terrific GUI for exercising an API
1. [HTTPie](https://httpie.org/) -- simple and powerful command-line client;
   easier to use than `curl` because is just does HTTP requests
   For example:
   ```bash
   $ http localhost:5000/members
   ```
1. [curl](https://curl.haxx.se/) -- exhaustive (exhausting?) command-line
   client; does _everything_; harder to learn than HTTPie.
   For example:
   ```bash
   $ curl http://localhost:5000/members
   ```
1. Write code.
- For Python, use [Requests](http://docs.python-requests.org/en/latest/);
   see the `test_api.py` file fo examples
- For Node, I like [Axios](https://www.npmjs.com/package/axios)
   