from labloom.logger import logger


def cli():
    logger.info("Running CLI mode.")
    print("Welcome to labloom CLI!")
    # Add CLI logic here
    from .examples.E08_drafter import run as processor_run

    processor_run()


def gui():
    logger.info("Running GUI mode.")
    print("Welcome to labloom GUI!")
    # Add GUI logic here


def main():
    logger.info("Hello from tool-ai-lab-generation-iiith!")
    logger.debug("This is a debug message.")
    logger.error("This is an error message.")
    logger.warning("This is a warning message.")
    logger.critical("This is a critical message.")
    print("Hello from tool-ai-lab-generation-iiith!")


if __name__ == "__main__":
    main()
