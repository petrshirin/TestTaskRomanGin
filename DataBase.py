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
        await self.conn.execute('''CREATE TABLE posts (id SERIAL PRIMARY KEY,
                                                 title VARCHAR(60),
                                                 body VARCHAR(2000),
                                                 author VARCHAR(30),
                                                 created_at TIMESTAMP)''')

    async def get_all_posts(self):
        rows = await self.conn.fetch('''SELECT * FROM posts''')
        return self.post_record_to_json(rows)

    async def get_post(self, post_id):
        rows = await self.conn.fetch('''SELECT * FROM posts WHERE id=$1''', post_id)
        if rows == []:
            return []
        return self.post_record_to_json(rows)[0]

    async def create_post(self, data):
        try:
            # return list with <Record id='post_id'>
            post_id = await self.conn.fetch(f'''INSERT INTO posts (title, body, author, created_at) 
                                                VALUES ($1, $2, $3, TIMESTAMP '{data['created_at']}') RETURNING id''',
                                            data['title'], data['body'], data['author'])
            data['id'] = post_id[0].get('id')
            return data
        except Exception as err:
            print(err)
            return None

    async def edit_post(self, data, post_id):
        try:
            await self.conn.fetch(f'''UPDATE posts SET title = $1,
                                                         body = $2,
                                                         author = $3,
                                                         TIMESTAMP '{data['created_at']}'
                                        WHERE id = $4''',
                                  data['title'], data['body'], data['author'], post_id)
            data['id'] = post_id
            return data
        except Exception as err:
            print(err)
            return None

    @staticmethod
    def post_record_to_json(data):
        data_json = []
        for row in data:
            post_json = {}
            for key in row.keys():
                if key == 'created_at':
                    post_json[key] = datetime.datetime.strftime(row.get(key), "%Y-%m-%dT%H:%M:%S.%fZ")
                    continue
                post_json[key] = row.get(key)
            data_json.append(post_json)
        return data_json

    async def close(self):
        await self.conn.close()
