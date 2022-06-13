from logging import getLogger
import sys
import os
sys.path.append(os.getcwd())

import time
from datetime import date
from crontab import CronTab
from docs.config import getConfig
from helper import check_dependencies, save_report, get_last_job_date
from logger.logger import get_logger

logger = get_logger()
config = getConfig()
entry = CronTab(config.get('DEFAULT', 'run_at'))
run_at_start = config.getboolean('DEFAULT', 'run_at_start')
# print(entry.next().strftime('%Y-%m-%d'))

def allow_to_run():
    # check today is the date that matches crontab setting
    # parse date from report and verify if it's a duplicated job
    target_job_date = entry.next(default_utc=True, return_datetime=True).strftime('%Y-%m-%d')
    last_date = get_last_job_date()
    today = date.today().strftime('%Y-%m-%d')
    return target_job_date == today and last_date != today

if __name__ == "__main__":
    logger.info('dependency check app runs')
    if run_at_start:
        logger.info('run at start')
        check_result = check_dependencies()
        save_report(check_result)
    while True:
        if allow_to_run():
            check_result = check_dependencies()
            save_report(check_result)
        time.sleep(1)