from dotenv import load_dotenv
from labloom.logger import logger
import os

load_dotenv()



def cli():
    """Run in CLI mode."""
    logger.info("Running CLI mode.")
    print("Welcome to labloom CLI (New)!")
    from .examples.langgraph.E08_drafter import run as processor_run
    processor_run()

def gui():
    """Run in GUI mode."""
    logger.info("Running GUI mode.")
    print("Welcome to labloom GUI!")

    try:
        from streamlit.web.bootstrap import run
        from . import streamlit_app as app  # must be in the same directory or PYTHONPATH

        run(app.__file__, False, [], {
            "server.enableStaticServing": True,
        })
    except Exception as e:
        logger.error(f"Failed to launch GUI: {e}")
        print("Error: Could not start GUI.")