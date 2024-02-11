import appdaemon.plugins.hass.hassapi as hass
import os
import sys
from loguru import logger
import requests
from bs4 import BeautifulSoup
import json

# vars
output_file = "monthly_payment_info.json"
main_Url = "https://www.alberta.ca/aish-and-income-support-payment-date-change"
table_selector = "#goa-band6166 > div:nth-child(1) > div.goa-tableouter > div > table"
months = []
payment_dates = []
days_between_payments = []
monthly_info = []

# Create logs folder
if not os.path.exists("logs"):
    os.makedirs("logs")

# Clear logs file
log_directory = os.path.join("appdaemon", "apps", "autoaish", "logs")
log_file = os.path.join(log_directory, "debug.log")
open(log_file, "w").close()

logger.add(log_file, level="DEBUG", rotation="10 MB")

def scrape_data():
    logger.debug("Starting scrape data function")
    response = requests.get(main_Url)

    if response.status_code == 200:
        logger.debug(response)
        soup = BeautifulSoup(response.content, "html.parser") # type: ignore
        logger.debug(f"Soup: {soup}")
        table_div = soup.find("div", class_="goa-table")
        if table_div:
            logger.debug(f"Table found: {table_div}")
            # Extract data from table rows
            for i, row in enumerate(table_div.find_all('tr')[1:], start=1):  # Skip the header row # type: ignore
                columns = row.find_all('td')
                if len(columns) >= 3:  # Check if the row has at least three columns
                    month = columns[0].text.strip()
                    # Extracting payment date and days between payments together
                    payment_date = columns[1].find(text=True, recursive=False).strip()
                    days_between = columns[2].text.strip()
                    months.append(month)
                    payment_dates.append(payment_date)
                    days_between_payments.append(days_between)
                else:
                    logger.debug(f"Ignoring row with insufficient columns: {columns}")
        else:
            logger.debug(f"NO TABLE FOUND")
    else:
        logger.debug(response)

def save_data():
    logger.debug("Starting Save Data Function")
    monthly_data = list(zip(months, payment_dates, days_between_payments))
    logger.debug(f"Monthly Data: {monthly_data}")
    for month, payment_date, days_between in monthly_data:
        monthly_info.append({
            "Month": month,
            "Payment Date": payment_date,
            "Days Between Payments": days_between
        })
    
    # Save the list of dictionaries into a JSON file
    with open(output_file, "w") as f:
        json.dump(monthly_info, f, indent=4)
    save_data_path = os.path.join(output_file)
    logger.debug(f"Saved file to: {save_data_path}")

scrape_data()
logger.debug(f"Months: {months}")
logger.debug(f"Payment Dates: {payment_dates}")
logger.debug(f"Days Between Payments: {days_between_payments}")
save_data()