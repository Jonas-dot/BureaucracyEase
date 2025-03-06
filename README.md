# BureaucracyEase - Appointment Scraper and Notifier

## Overview
BureaucracyEase is a web-based appointment scraper and notifier for Berlin's public service platform, `service.berlin.de`. The application scrapes appointment availability for various services in Berlin, such as visa appointments, and sends real-time updates to users when new appointments are available.

This project uses a combination of Flask for the backend and WebSocket for real-time updates. The frontend (currently in progress) displays scraped appointments and allows users to trigger scraping and fetch the latest available appointments.

## Key Features
- Scrapes appointment availability from Berlin's official website.
- Real-time notifications via WebSocket when new appointments are found.
- Frontend to fetch and display appointment data.
- Basic backend architecture with SQLite for storing appointments.

## Installation

### Prerequisites
To run this project, you need the following tools installed:
- Python 3.x
- Node.js (for running the frontend)
- pip (Python package manager)
- An IDE or text editor (e.g., Visual Studio Code)

### Backend Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/YourUsername/BureaucracyEase.git
    cd BureaucracyEase
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # On Windows use .venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    - Ensure you have a local SQLite database or modify the `database.py` to connect to your desired database.
    - The backend fetches service URLs from this database.

5. Run the backend:
    ```bash
    python app.py
    ```

    This will start the Flask server at `http://127.0.0.1:5000` and the WebSocket server at `ws://127.0.0.1:8765`.

### Frontend Setup

1. Navigate to the `frontend` directory (if it exists):
    ```bash
    cd frontend
    ```

2. If needed, install dependencies for the frontend (e.g., if using a framework like React or plain HTML, CSS, and JS, you can directly include them):
    ```bash
    npm install
    ```

3. Open `index.html` in your browser. Ensure the backend is running so that the frontend can fetch data and communicate via WebSocket.

### Configuration
- Modify the `get_service_urls_from_db()` function in the `app.py` to match your database schema or add service URLs directly in the database.
- Adjust `email` and `script_id` in the `watch_for_appointments()` function in `app.py` to match your setup for scraping.

## Features in Progress
- **Frontend**: The frontend is in an early stage, with basic functionality to display appointment data. The UI could be further improved for better user experience.
- **Appointment Scraping**: The scraper currently fetches available appointments from the Berlin website but needs a robust error-handling mechanism for reliability.

## Known Issues
- The frontend is a simple static page and doesn't yet have full integration with the backend. Features like displaying real-time updates and an interactive UI are still a work in progress.
- The WebSocket server might experience issues if multiple services are being scraped at the same time, causing potential connection problems. You may need to add more handling to ensure the WebSocket server handles multiple connections smoothly.

## Code Overview

### Backend (`app.py`)
- **Flask**: Used to serve the backend API for fetching appointments and starting scraping manually.
- **WebSocket**: Used to notify all connected clients (via `SocketIO` and `websockets`) when new appointments are found.
- **Scraper**: The `scrape_appointments` function scrapes appointment data from the Berlin service website. It is integrated with Flask endpoints to trigger scraping manually.
- **Queue**: An `asyncio.Queue` is used to pass data from the appointment scraper tasks to the WebSocket server for broadcasting updates.

### Frontend (`index.html`, `script.js`)
- The frontend is a simple HTML page with JavaScript for fetching appointment data and displaying it on the page.
- It includes:
  - **Fetch Button**: To request the latest appointment data from the backend and display it.
  - **Scrape Button**: To trigger manual scraping of appointments.
  - **WebSocket**: To receive real-time updates from the backend when new appointments are available.

### External Libraries
- **Flask**: For the backend API.
- **Flask-SocketIO**: For WebSocket communication with clients.
- **aiohttp**: For asynchronous HTTP requests used in scraping appointments.
- **BeautifulSoup**: For parsing HTML and extracting appointment data.
- **WebSockets**: For handling real-time updates to clients.

## How it Works

1. **Backend Scraping**:
   - The backend continuously scrapes available appointment data from Berlin's public service platform.
   - It then sends real-time updates to connected clients via WebSocket when new appointments are found.
   
2. **Frontend**:
   - The frontend allows users to request the latest appointment data by clicking a button.
   - It displays the fetched appointments in a simple list, showing important details like the appointment date, status, and additional info.
   
3. **Real-time Updates**:
   - Whenever an appointment is found or updated, the backend sends the new data to the frontend via WebSocket, allowing the page to update without refreshing.

## Code from External Sources
This project uses portions of code taken from [burgeramt-appointments](https://github.com/All-About-Berlin/burgeramt-appointments), specifically the scraping logic for fetching appointment data. The code has been modified and extended to fit the needs of this project, including adding WebSocket support and integrating the scraping process with Flask.

## Future Enhancements
- **UI Improvements**: The frontend can be enhanced with better styling and interactive features like filtering, pagination, and user authentication.
- **Error Handling**: Implement better error handling in the scraping functions to deal with potential timeouts or changes in the structure of the Berlin service pages.
- **Scheduled Scraping**: Automate the scraping process to periodically check for appointments, rather than relying on manual triggers.

---

**Disclaimer**: This project is not affiliated with or endorsed by the Berlin government. It is a tool for simplifying the process of finding appointments on `service.berlin.de`. Use at your own discretion.