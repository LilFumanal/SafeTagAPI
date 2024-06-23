"""
ASGI config for SafeTag project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import asyncio
import logging
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SafeTag.settings")

application = get_asgi_application()

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all types of log messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.StreamHandler(),  # Log to stderr (console)
        logging.FileHandler("app.log", mode='a'),  # Log to a file (append each time)
    ]
)

def sync_cancel_pending_tasks():
    # Get the current event loop
    loop = asyncio.get_running_loop()
    
    # Gather all tasks excluding the current one
    tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task(loop)]
    
    if not tasks:
        print("No pending tasks to cancel.")
        return
    
    print(f"Cancelling {len(tasks)} pending tasks synchronously...")

    for task in tasks:
        task.cancel()

    # Run until all tasks are cancelled
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    print("All pending tasks have been cancelled.")

# Example usage: Call this function before shutdown or during a critical section
# sync_cancel_pending_tasks()