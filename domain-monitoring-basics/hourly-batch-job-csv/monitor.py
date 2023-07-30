import os
import datetime
import logging

import textdistance as td

from api import get_token, get_domains_csv_streamer

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# todo: Adjust your threshold based on your metrics
MINIMUM_THRESHOLD = 2


def alert(your_domain: str, ct_log_domain: str) -> None:
    # todo: Add your own alerting here!
    logger.info(f"Heads up! {ct_log_domain} is very similar to {your_domain} ...")
    return None


def metric(your_domain: str, ct_log_domain: str) -> float:
    # todo: Add your own similarity metrics/functions here!
    distance = td.levenshtein(your_domain, ct_log_domain)
    return distance


def get_previous_date_and_hour_utc() -> str:
    dt = datetime.datetime.utcnow()
    # get last hour
    dt = dt - datetime.timedelta(hours=1)
    return dt.strftime("%Y-%m-%d-%H")  # e.g. "2023-06-01-16" or 2023-06-01 16:00:00


def process_csv_row(your_domain: str, row: bytes) -> None:
    # decode and split row by comma
    data = row.decode().split(",")
    # domain_name is the first column
    ct_log_domain = data[0]
    # compare the ct_log_domain to your_domain
    value = metric(your_domain, ct_log_domain)
    # if the similarity threshold is exceeded, create alert!
    if value < MINIMUM_THRESHOLD:
        alert(your_domain, ct_log_domain)


def monitor_hourly(your_domain: str, date_and_hour: str | None) -> None:
    # get an access token
    token = get_token(client_id, client_secret)
    # check if date_and_hour was given
    if date_and_hour is None:
        date_and_hour = get_previous_date_and_hour_utc()
    # process the last hour of domains
    domains_csv = get_domains_csv_streamer(token, date_and_hour)
    header_row = True
    count = 0
    for row in domains_csv:
        # skip header row
        if header_row:
            header_row = False
            continue
        # handle each row
        process_csv_row(your_domain, row)
        # keep count of rows
        count += 1
        if count % 1000 == 0:
            logger.info(f"Finished processing {count} rows...")
    