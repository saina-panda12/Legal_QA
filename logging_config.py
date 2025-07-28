import logging

# Setting up logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Log messages that are INFO or higher (e.g., WARNING, ERROR)
        format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
        handlers=[
            logging.FileHandler("logs/app.log"),  # Log messages to a file
            logging.StreamHandler()  # Also print log messages to the console
        ]
    )
