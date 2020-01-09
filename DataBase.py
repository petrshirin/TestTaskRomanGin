import asyncio
import asyncpg
from config import *


class DataBase:

    def __init__(self):
        self.conn = None

    async def connection(self, pool):
        self.conn = pool
        print(dir(self.conn))

    async def create_table(self):
        await self.conn.execute('''CREATE TABLE posts (id SERIAL PRIMARY KEY,
                                                 title VARCHAR(60),
                                                 body VARCHAR(2000),
                                                 author VARCHAR(30),
                                                 created_at TIMESTAMP WITH TIME ZONE)''')

    async def get_all_posts(self):
        rows = await self.conn.fetch('''SELECT * FROM posts''')
        return rows

    async def get_post(self, post_id):
        row = await self.conn.fetch('''SELECT * FROM posts WHERE id=$1''', post_id)
        return row

    async def create_post(self, data):
        try:
            await self.conn.execute(f'''INSERT INTO posts (title, body, author, created_at) 
                                       VALUES ($1, $2, $3, TIMESTAMP '{data['created_at']}')''',
                                    data['title'], data['body'], data['author'])
            return True
        except Exception as err:
            print(err)
            return False

    async def edit_post(self, data, post_id):
        try:
            await self.conn.execute(f'''UPDATE posts SET title = $1,
                                                         body = $2,
                                                         author = $3,
                                                         TIMESTAMP '{data['created_at']}'
                                        WHERE id = $4''',
                                    data['title'], data['body'], data['author'], post_id)
            return True
        except Exception as err:
            print(err)
            return False

    async def close(self):
        await self.conn.close()


