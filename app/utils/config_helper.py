import argparse
from app.utils.logging_helper import logger
from app.core.configuration import AppConfig
import sys

from omegaconf import DictConfig


def get_config() -> DictConfig:
    # Load configuration from command line
    logger.info('Loading configuration environment')
    parser = argparse.ArgumentParser(description="CLI tool to load application configuration environments from the command line.")
    parser.add_argument("environment", type=str, help="Usage: python main.py [dev|staging|prod]")
    args = parser.parse_args()
    
    # Ensure a valid command line argument is provided
    if args.environment not in ["dev", "staging", "prod"]:
        logger.error("Usage: python main.py [dev|staging|prod]")
        sys.exit(1)

    # Load the configuration based on the provided environment
    app_config = AppConfig(args.environment)
    cfg = app_config.load_config()
    return cfg
