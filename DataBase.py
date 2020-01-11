import asyncio
import asyncpg
from config import *
import datetime


class DataBase:

    def __init__(self):
        self.conn = None

    async def connection(self, pool):
        self.conn = pool
        print(dir(self.conn))

    async def init_database(self):
        await self.conn.execute('''CREATE TABLE authors (id SERIAL PRIMARY KEY,
                                                         author_name VARCHAR(30))''')

        await self.conn.execute('''CREATE TABLE posts (id SERIAL PRIMARY KEY,
                                                 title VARCHAR(60) NOT NULL,
                                                 body VARCHAR(2000) NOT NULL,
                                                 author INTEGER REFERENCES authors (id) ON DELETE CASCADE,
                                                 created_at TIMESTAMP,
                                                 deleted BOOLEAN DEFAULT FALSE)''')

    async def get_all_posts(self):
        rows = await self.conn.fetch('''
        SELECT (posts.id, posts.title, posts.body, authors.author_name, posts.created_at) 
        FROM posts LEFT JOIN authors ON posts.author = authors.id
        WHERE posts.deleted = FALSE''')
        return self.post_record_to_json(rows)

    async def get_post(self, post_id):
        rows = await self.conn.fetch('''
        SELECT (posts.id, posts.title, posts.body, authors.author_name, posts.created_at) 
        FROM posts LEFT JOIN authors ON posts.author = authors.id
        WHERE posts.id=$1 and posts.deleted = FALSE''', post_id)

        if rows == []:
            return []
        return self.post_record_to_json(rows)[0]

    async def create_post(self, data):
        try:
            authors = await self.conn.fetch(f'''SELECT * FROM authors''')
            author_id = None
            for author in authors:
                if author.get('author_name') == data['author']:
                    author_id = author.get('id')
            if not author_id:
                return None

            # return list with <Record id='post_id'>
            post_id = await self.conn.fetch(f'''INSERT INTO posts (title, body, author, created_at) 
                                                VALUES ($1, $2, $3, TIMESTAMP '{data['created_at']}') RETURNING id''',
                                            data['title'], data['body'], author_id)
            data['id'] = post_id[0].get('id')
            return data
        except Exception as err:
            print(err)
            return None

    async def edit_post(self, data, post_id):
        try:
            authors = await self.conn.fetch(f'''SELECT * FROM authors''')
            author_id = None
            for author in authors:
                if author.get('author_name') == data['author']:
                    author_id = author.get('id')
            if not author_id:
                return None
            await self.conn.fetch(f'''UPDATE posts SET title = $1,
                                                         body = $2,
                                                         author = $3,
                                                         created_at = TIMESTAMP '{data['created_at']}' 
                                      WHERE id = $4''',
                                  data['title'], data['body'], author_id, post_id)
            data['id'] = post_id
            return data
        except Exception as err:
            print(err)
            return None

    async def delete_post(self, post_id):
        try:
            await self.conn.fetch(f'''UPDATE posts SET deleted = TRUE WHERE id = $1''', post_id)
            return True
        except Exception as err:
            print(err)
            return False

    @staticmethod
    def post_record_to_json(data):
        data_json = []
        for row in data:
            post_json = {}
            post_json['id'] = row.get('row')[0]
            post_json['title'] = row.get('row')[1]
            post_json['body'] = row.get('row')[2]
            post_json['author'] = row.get('row')[3]
            post_json['created_at'] = datetime.datetime.strftime(row.get('row')[4], "%Y-%m-%dT%H:%M:%S.%fZ")
            data_json.append(post_json)
        return data_json

    async def close(self):
        await self.conn.close()
