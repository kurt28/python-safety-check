import yaml
import logging
import logging.config

with open('logger/logger.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger('dependencyCheck')

def get_logger():
    return logger