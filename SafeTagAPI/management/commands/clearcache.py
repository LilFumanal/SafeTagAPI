import asyncio
from django.core.management.base import BaseCommand
from aiocache import caches


class Command(BaseCommand):
    help = "Clear the caches manually"
    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.clear_caches())
        self.stdout.write(self.style.SUCCESS("Successfully cleared caches"))

    async def clear_caches(self):
        cache = caches.get('default')
        await cache.clear()