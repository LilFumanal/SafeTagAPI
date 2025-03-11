import asyncio
import pytest
from unittest.mock import patch, MagicMock
from django.core.handlers.asgi import ASGIHandler, ASGIRequest
from django.http import HttpResponse
from asgiref.testing import ApplicationCommunicator

# SafeTag/test_asgi.py

def sync_cancel_pending_tasks():
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task(loop)]
    if not tasks:
        print("No pending tasks to cancel.")
        return
    print(f"Cancelling {len(tasks)} pending tasks synchronously...")
    for task in tasks:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    print("All pending tasks have been cancelled.")

@pytest.fixture
def asgi_handler():
    return ASGIHandler()

@pytest.mark.asyncio
@patch('SafeTagAPI.tests.test_asgi.sync_cancel_pending_tasks')
async def test_sync_cancel_pending_tasks(mock_cancel):
    loop = asyncio.get_event_loop()
    loop.call_soon(sync_cancel_pending_tasks)
    await asyncio.sleep(0.1)
    mock_cancel.assert_called_once()

@pytest.mark.asyncio
async def test_asgi_handler(asgi_handler, settings):
    settings.ALLOWED_HOSTS = ['unknown']
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/',
        'headers': [],
    }
    communicator = ApplicationCommunicator(asgi_handler, scope)
    await communicator.send_input({'type': 'http.request'})
    response = await communicator.receive_output()
    assert response['status'] == 200

if __name__ == '__main__':
    pytest.main()