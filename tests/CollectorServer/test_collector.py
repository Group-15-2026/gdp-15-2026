from geo_agent.CollectorServer.collector import get_daily_articles, get_articles_about, create_tables

import datetime

#import pytest

def main():
    create_tables()

    print(get_daily_articles())

    print(get_articles_about(["trade"], datetime.datetime.today(), datetime.datetime.today()-datetime.timedelta(days=1)))

if __name__ == "__main__":
    main()