from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
import re
import requests
from database import session, Service  # Import session and Service model
from sqlalchemy.exc import IntegrityError

# Logging configuration
# logging.basicConfig(level=logging.DEBUG)


def scrape_appointments():
    # Initialize the WebDriver for Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Invisible browser mode
    service = ChromeService(
        executable_path="C:/ProgramData/chocolatey/bin/chromedriver.exe")

    # Open the browser and go to the service page
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://service.berlin.de/dienstleistung/")  # URL to scrape

    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all service links
    services = soup.find_all("a", href=True)

    # Iterate over the services and check availability
    for service in services:
        service_url = service['href']
        if "dienstleistung" in service_url and "https://service.berlin" in service_url:
            # Ensure the URL is absolute
            service_url = urljoin("https://service.berlin.de", service_url)

            try:
                # Extract service number from the URL
                match = re.search(r'/(\d+)/$', service_url)
                if match:
                    number = match.group(1)  # Extract service number
                    name = service.text.strip()  # Get the name of the service

                    # Check if the service has available appointments (not 404)
                    new_url = f"https://service.berlin.de/terminvereinbarung/termin/all/{number}"
                    response = requests.get(new_url, allow_redirects=True)

                    if response.status_code != 404:  # Only consider services with available appointments
                        # Create a Service object and add to session
                        service_obj = Service(
                            number=number,
                            name=name,
                            service_url=service_url
                        )
                        session.add(service_obj)  # Add service to session

            except IntegrityError as e:
                # Ignore duplicate entries
                logging.warning(f"Duplicate service found: {e}")
                session.rollback()  # Rollback the current transaction to avoid issues
            except Exception as e:
                logging.error(f"Error processing URL {service_url}: {e}")

    # Commit all the valid services to the database
    try:
        session.commit()
        logging.debug(f"Successfully saved services to the database.")
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to save services to the database: {e}")

    driver.quit()  # Close the Selenium browser

    return "Services scraped and stored successfully."
