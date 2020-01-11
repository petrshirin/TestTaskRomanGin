import asyncio
from aiohttp import web
import asyncpg
from config import *
from DataBase import DataBase


async def init_app():
    app = web.Application()
    app['pool'] = await asyncpg.create_pool(db_url)

    app.router.add_route('GET', '/', welcome)
    app.router.add_route('GET', '/posts', get_posts)
    app.router.add_route('GET', '/posts/{id}', get_post)
    app.router.add_route('POST', '/posts', create_post)
    app.router.add_route('PUT', '/posts/{id}', edit_post)
    app.router.add_route('DELETE', '/posts/{id}', delete_post)
    return app


async def get_posts(request):
    db = DataBase()
    await db.connection(request.app['pool'])
    posts = await db.get_all_posts()
    print(posts)

    if posts:
        return web.json_response(posts, status=200)
    else:
        return web.Response(status=400, text="Некорректные данные")


async def get_post(request):
    db = DataBase()
    try:
        post_id = int(request.match_info['id'])
    except ValueError:
        return web.Response(status=400, text="Некорректные данные")

    await db.connection(request.app['pool'])
    post = await db.get_post(post_id)
    print(post)
    if post:
        return web.json_response(post, status=200)
    else:
        return web.Response(status=400, text="Некорректные данные")


async def create_post(request):
    db = DataBase()
    data = await request.json()
    await db.connection(request.app['pool'])

    if not validate_data(data):
        return web.Response(status=400, text="Некорректные данные")

    post = await db.create_post(data)
    print(post)

    if post is not None:
        return web.json_response(post, status=201)
    else:
        return web.Response(status=400, text="Некорректные данные")


async def edit_post(request):
    db = DataBase()
    await db.connection(request.app['pool'])

    try:
        post_id = int(request.match_info['id'])
    except ValueError:
        return web.Response(status=400, text="Некорректные данные")
    data = await request.json()
    if not validate_data(data):
        return web.Response(status=400, text="Некорректные данные")

    post = await db.edit_post(data, post_id)
    if post:
        return web.json_response(post, status=200)
    else:
        return web.Response(status=400, text="Некорректные данные")


async def delete_post(request):
    db = DataBase()
    await db.connection(request.app['pool'])

    try:
        post_id = int(request.match_info['id'])
    except ValueError:
        return web.Response(status=400, text="Некорректные данные")

    result = await db.delete_post(post_id)

    if result:
        return web.Response(status=204)
    else:
        return web.Response(status=400, text="Некорректные данные")


async def welcome(request):
    try:
        db = DataBase()
        await db.connection(request.app['pool'])
        await db.init_database()
    except Exception as err:
        print(err)
        pass
    return web.json_response({'status': 'service is worked'})


async def validate_data(data):
    for val in data.values():
        if len(val) < 1:
            return False
    return True

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init_app())
web.run_app(app, host="127.0.0.1", port=8000)
