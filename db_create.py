#!/usr/bin/python3
'''
Create a database for the Twitter project.
'''

# sqlite3 is built in python3, no need to pip install
import sqlite3
import random
from datetime import datetime, timedelta

# process command line arguments
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

# connect to the database
con = sqlite3.connect(args.db_file)   # con, conn = connection; always exactly 1 of these variables per python project
cur = con.cursor()                    # cur = cursor; for our purposes, exactly 1 of these per python file

# create the users table
sql = '''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER
);
'''
cur.execute(sql)
con.commit()

# create the messages table
sql = '''
create table messages (
    id integer primary key,
    sender_id integer not null,
    message text not null,
    created_at timestamp not null default current_timestamp,
    edited_at timestamp
    );
'''
cur.execute(sql)
con.commit()

subjects = ['I', 'We', 'They', 'My roommate', 'The professor', 'She', 'He', 'Bob', 'Mike', 'The three-headed bear', 'My dinosaur', 'Woody']
verbs = ['love', "can't", 'hate', 'study', 'recommend', 'miss', 'use', 'find', 'slide', 'race', 'eat', 'despise', 'doodle', 'squabble', 'discombobulate']
objects = ['SQL', 'FastAPI', 'matcha', 'Python', 'sleep', 'databases', '"double quote"', 'cert10', 'https://google.com', 'flowers', 'minions']
punctuation = ['!', '.', '...', '?']

for user_num in range(220):
    username = f'user{user_num}'
    password = f'password{user_num}'
    age = random.randint(1, 100)

    cur.execute(
        '''
        INSERT INTO users (username, password, age)
        VALUES (?, ?, ?);
        ''',
        [username, password, age]
    )

    user_id = cur.lastrowid

    for message_num in range(220):

        message = (
            f'{random.choice(subjects)} '
            f'{random.choice(verbs)} '
            f'{random.choice(objects)}'
            f'{random.choice(punctuation)} '
        )

        cur.execute(
            '''
            INSERT INTO messages (sender_id, message)
            VALUES (?, ?);
            ''',
            [user_id, message]
        )

con.commit()