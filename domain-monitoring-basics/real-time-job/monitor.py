import os
import logging
import time

import requests
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


def monitor_domains(domain_name: str, token: str, start_from_id: str = None) -> str:
    # url params
    params = {"limit": 1000}
    if start_from_id is not None:
        params["start_from_id"] = start_from_id

    # make request for domains
    domains_response = get_domains(token, params)

    # make sure there were new domains
    if len(domains_response["domains"]) == 0:
        # nothing new, return the same starting id
        logger.info("The latest start_from_id did not change...")
        return start_from_id

    # check the domains
    check_domains(domains_response["domains"], domain_name)

    # all latest domains from the last request have now been checked,
    # and alerts generated for any that were similar to your_domain

    if start_from_id is None:
        # if this is the "first" call, return the last id to be used
        # as the `start_from_id` in next the function call
        next_start_id = domains_response["domains"][0]["id"]
    else:
        # otherwise, use the last id as parameter to the next call
        next_start_id = domains_response["domains"][-1]["id"]

    return next_start_id


def monitor_continuously(domain_name: str) -> None:
    # get an access token
    token = get_token(client_id, client_secret)
    # set start id to null, so we begin with the latest domains
    start_id = None
    # run forever
    while True:
        try:
            # update start_id to request the latest domains
            start_id = monitor_domains(domain_name, token=token, start_from_id=start_id)
            # pause for a second to avoid rate-limit errors
            logger.info("Waiting 1 second(s) before fetching next batch.")
            time.sleep(1.0)

        except requests.exceptions.HTTPError as e:
            # catch expired token errors
            if e.response.status_code in [401, 403]:
                # get a new token and retry
                token = get_token(client_id, client_secret)
            else:
                raise e