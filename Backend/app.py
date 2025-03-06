from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from scraper import scrape_appointments
from database import save_appointments, get_appointments_new, session, Service
from models import Appointment, Service
import asyncio
import logging
from datetime import datetime
import pytz
import chime
import aiohttp
import websockets
import queue
from bs4 import BeautifulSoup, SoupStrainer

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='eventlet')

# Configure logging
logger = logging.getLogger(__name__)
chime.theme('material')

# Constants
refresh_delay = 180  # Minimum allowed by Berlin.de's IKT-ZMS team.
timezone = pytz.timezone('Europe/Berlin')

# Variables for managing WebSocket clients and the last known message
connected_clients = []
last_message = {
    'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'status': 200,
    'appointmentDates': [],
    'lastAppointmentsFoundOn': None,
}

# Create an asyncio queue to share data between tasks and WebSocket server
appointment_queue = asyncio.Queue()


def datetime_to_json(datetime_obj: datetime) -> str:
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_headers(email: str, script_id: str) -> dict:
    return {
        "User-Agent": "Mozilla/5.0",
        "X-Email": email,
        "X-Script-Id": script_id,
    }


# Scraping function to get appointments from Berlin.de
async def get_appointments(appointments_url: str, email: str, script_id: str) -> list:
    today = timezone.localize(datetime.now())
    next_month = timezone.localize(
        datetime(today.year, today.month % 12 + 1, 1))
    next_month_timestamp = int(next_month.timestamp())

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(appointments_url, headers=get_headers(email, script_id), timeout=20) as response_page1:
            page1_dates = parse_appointment_dates(await response_page1.text())

        page2_url = f'https://service.berlin.de/terminvereinbarung/termin/day/{next_month_timestamp}/'
        async with session.get(page2_url, headers=get_headers(email, script_id), timeout=20) as response_page2:
            page2_dates = parse_appointment_dates(await response_page2.text())

    return sorted(list(set(page1_dates + page2_dates)))


def parse_appointment_dates(page_content: str) -> list:
    appointment_strainer = SoupStrainer('td', class_='buchbar')
    bookable_cells = BeautifulSoup(
        page_content, 'html.parser', parse_only=appointment_strainer).find_all('a')
    appointment_dates = []
    for bookable_cell in bookable_cells:
        timestamp = int(bookable_cell['href'].rstrip('/').split('/')[-1])
        appointment_dates.append(timezone.localize(
            datetime.fromtimestamp(timestamp)))

    return appointment_dates


# Function to fetch appointments and put updates into the queue
async def look_for_appointments(appointments_url: str, email: str, script_id: str, quiet: bool) -> dict:
    try:
        appointments = await get_appointments(appointments_url, email, script_id)
        logger.info(f"Found {len(appointments)} appointments.")
        if len(appointments) and not quiet:
            chime.info()

        return {
            'time': datetime_to_json(datetime.now()),
            'status': 200,
            'message': None,
            'appointmentDates': [datetime_to_json(d) for d in appointments],
        }
    except Exception as e:
        logger.exception("Error fetching appointments.")
        if not quiet:
            chime.error()

        return {
            'time': datetime_to_json(datetime.now()),
            'status': 500,
            'message': f'Error: {str(e)}',
            'appointmentDates': [],
        }


@socketio.on('connect')
def on_connect():
    global last_message
    connected_clients.append(request.sid)
    emit('appointments_update', last_message)


# WebSocket server handler for all appointment updates
async def websocket_handler(websocket, path):
    while True:
        # Get the next appointment update from the shared queue
        appointment_data = await appointment_queue.get()
        await websocket.send(appointment_data)


async def watch_for_appointments(service_page_url: str, email: str, script_id: str, quiet: bool):
    appointments_url = f"https://service.berlin.de/terminvereinbarung/termin/all/{service_page_url.split('/')[-1]}/"
    while True:
        last_appts_found_on = last_message['lastAppointmentsFoundOn']
        new_message = await look_for_appointments(appointments_url, email, script_id, quiet)

        # Update last known message
        if new_message['appointmentDates']:
            new_message['lastAppointmentsFoundOn'] = datetime_to_json(
                datetime.now())
        else:
            new_message['lastAppointmentsFoundOn'] = last_appts_found_on

        # Put the new message into the shared queue
        await appointment_queue.put(new_message)

        # Emit the update to all connected clients via Flask-SocketIO
        for client in connected_clients:
            socketio.emit('appointments_update', new_message, room=client)

        await asyncio.sleep(refresh_delay)


def get_service_urls_from_db():
    services = session.query(Service).all()
    return [service.service_url for service in services]


async def start_background_tasks():
    service_urls = get_service_urls_from_db()

    # Create tasks for each service URL
    tasks = []
    for service_url in service_urls:
        print("Looking for appointments at", service_url)
        tasks.append(asyncio.create_task(watch_for_appointments(
            service_url, "your_email@example.com", "your_script_id", False)))

    # Ensure that all tasks run concurrently
    await asyncio.gather(*tasks)


# Start background tasks and Flask app
if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Start background tasks
    asyncio.run(start_background_tasks())

    print("Starting the WebSocket server")  # Debugging point

    # Start the WebSocket server (only once for all services)
    start_server = websockets.serve(websocket_handler, 'localhost', 8765)

    loop.run_until_complete(start_server)

    # Start the Flask-SocketIO server using the `asyncio` event loop
    print("Starting the Flask-SocketIO server")
    socketio.run(app, debug=True, port=5000)
