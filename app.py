import asyncio
from aiohttp import web
import asyncpg
from config import *
from DataBase import DataBase
from time import sleep

routes = web.RouteTableDef()


async def init_app():
    app = web.Application()
    app['pool'] = await asyncpg.create_pool(db_url)

    app.router.add_route('GET', '/', welcome)
    app.router.add_route('GET', '/posts', get_post)
    return app


async def get_post(request):
    db = DataBase()
    await db.connection(request.app['pool'])
    posts = await db.get_all_posts()
    print(posts)
    await db.close()
    return web.json_response({123: 123}, status=200)


async def create_post(request):
    db = DataBase()
    await db.connection(request.app['pool'])
    print(request)
    await db.close()


async def welcome(request):
    return web.json_response({'qwe': 'ewq'})

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init_app())
web.run_app(app, host="127.0.0.1", port=8000)
