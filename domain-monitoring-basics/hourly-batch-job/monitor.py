import os
import datetime
import logging

import textdistance as td

from api import get_token, get_domains

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# todo: Adjust your threshold based on your metrics
MINIMUM_THRESHOLD = 15


def alert(your_domain: str, ct_log_domain: str) -> None:
    # todo: Add your own alerting here!
    logger.info(f"Heads up! {ct_log_domain} is very similar to {your_domain} ...")
    return None


def metric(your_domain: str, ct_log_domain: str) -> float:
    # todo: Add your own similarity metrics/functions here!
    distance = td.levenshtein(your_domain, ct_log_domain)
    return distance


def check_domains(domains: list, your_domain: str) -> None:
    # iterate through the domains returned from certificate.stream
    for domain_obj in domains:
        # compare each to your_domain
        ct_log_domain = domain_obj["domain_name"]
        value = metric(your_domain, ct_log_domain)
        # if the similarity threshold is exceeded, create alert!
        if value < MINIMUM_THRESHOLD:
            alert(your_domain, ct_log_domain)
        else:
            logger.info(f"Ok. {ct_log_domain} is NOT similar to {your_domain} ...")


def get_previous_date_and_hour_utc():
    dt = datetime.datetime.utcnow()
    # get last hour
    dt = dt - datetime.timedelta(hours=1)
    return dt.strftime("%Y-%m-%d-%H")  # e.g. "2023-06-01-16" or 2023-06-01 16:00:00


def monitor_domains(domain_name: str, token: str, date_and_hour: str) -> None:
    # define url params
    params = {
        "limit": 1000,  # Fetch batches of 1000 domains at a time.
        "offset": 0,
        "date_and_hour": date_and_hour,
    }
    # make initial request for domains
    domains_response = get_domains(token, params)
    # domains_response schema: https://villain.network/docs/list-latest-domains

    # `count` is the total number of domains from the past hour
    count = domains_response["count"]
    logger.info(f"There are a total of {count} domains from the past hour.")

    # the offset used for this page of results (0)
    offset = domains_response["offset"]

    # check the first batch of domains
    check_domains(domains_response["domains"], domain_name)
    logger.info(f"Finished checking {offset+1000}/{count} domains.")

    # the `/list` endpoint uses offset-based pagination, so
    # we'll continue making calls with the offset parameter
    # until all domains from the past hour have been processed
    while (offset + 1000) < count:
        # update offset and re-request data
        offset += 1000
        params["offset"] = offset
        domains_response = get_domains(token, params)
        # check the domains
        check_domains(domains_response["domains"], domain_name)
        logger.info(f"Finished checking {offset+1000}/{count} domains.")

    # all domains from the previous hour have now been checked
    # and alerts generated for any that were similar to your_domain
    return


def monitor_previous_hour(domain_name: str, date_and_hour: str = None) -> None:
    # get an access token
    token = get_token(client_id, client_secret)
    # check if date_and_hour was given
    if date_and_hour is None:
        date_and_hour = get_previous_date_and_hour_utc()
    # process the last hour of domains
    monitor_domains(domain_name, token, date_and_hour)
    logger.info(f"Finished monitoring domains from {date_and_hour}.")
    return
