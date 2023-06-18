from monitor import monitor_previous_hour

YOUR_DOMAIN = "examplecompany.com"


if __name__ == "__main__":
    # TODO: you could use command line arguments to set date_and_hour
    date_and_hour = None  # None is a valid value, monitor_previous_hour will handle populating it
    monitor_previous_hour(YOUR_DOMAIN, date_and_hour=date_and_hour)
