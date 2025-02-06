import asyncio
from aiohttp import web
import nest_asyncio

# Apply nest_asyncio to support nested event loops
nest_asyncio.apply()

async def home(request):
    return web.Response(text="Telegram Bot is running on aiohttp server!")

async def init_app():
    app = web.Application()
    app.router.add_get('/', home)
    return app

async def start_web_server():
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour

if __name__ == '__main__':
    asyncio.run(start_web_server())
