import logging

def main():
    print("Hello from gdp-15-2026!")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    # XX Note: To create a logger for a file, you only need to import logging
    # and also write logger = logging.getLogger(__name__) in the file
    logger.info("Just checking in")
    main()
