import logging
import logging.config
import yaml
import os

_logging_configured = False

def log(message, error=False):
    """
    Log a message with proper console output using YAML configuration.
    
    Args:
        message (str): The message to log
        error (bool): If True, log as error, otherwise as info
    """
    global _logging_configured
    
    if not _logging_configured:
        configure_logging()
        _logging_configured = True
    
    logger = logging.getLogger(__name__)
    
    if error:
        logger.error(message)
    else:
        logger.info(message)

def configure_logging():
    """
    Configure logging from the YAML config file.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "logging.yaml")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
            
configure_logging()
_logging_configured = True
