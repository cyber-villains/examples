from monitor import monitor_hourly

YOUR_DOMAIN = "examplecompany.com"


if __name__ == "__main__":
    # TODO: you could use command line arguments to set date_and_hour

    # **Note**
    # To ensure consistency around handling late arriving data, the CSV file
    # for previous hour is available at the earliest 5 minutes after the hour.
    # For example, the domains from the hour 5:00AM-6:00AM would available at 6:05AM.

    date_and_hour = None  # None is a valid value, monitor_hourly will use the previous hour by default
    monitor_hourly(YOUR_DOMAIN, date_and_hour=date_and_hour)
