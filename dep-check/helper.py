import sys
import os
sys.path.append(os.getcwd())

import json
import re
from datetime import date
from pkginfo import Wheel

from docs.config import getConfig
from logger.logger import get_logger

config = getConfig()
report_path = config.get('DEFAULT', 'report_path')
logger = get_logger()

def get_dep_version(whl_file):
    package = Wheel(whl_file)
    return '{name}=={version}'.format(name=package.name, version=package.version)

def convert_check_result_to_dict(check_result):
    return {
        "package": check_result[0],
        "affected_version": check_result[1],
        "installed_version": check_result[2],
        "description": check_result[3],
        "vulnerability_id": check_result[4]
    }

def transform_batch_check_result(batch_check_result):
    if len(batch_check_result) == 0:
        return []
    else:
        return list(map(convert_check_result_to_dict, batch_check_result))

def batch_check_dependencies_by_safety(batch_whl_files):
    logger.info('batch_whl_files: {}'.format(batch_whl_files))
    batch_check_stream = os.popen('echo $\'{}\' | safety check --stdin --json'.format("\n".join(batch_whl_files)))
    batch_check_result = json.loads(batch_check_stream.read())
    return transform_batch_check_result(batch_check_result)

def check_dependencies():
    # find all whl files in dep_path
    dep_path = config.get('DEFAULT', 'dep_path')
    find_stream = os.popen('find {} -name "*.whl"'.format(dep_path))
    whl_files = find_stream.read().strip().split('\n')
    dep_version_list = list(map(get_dep_version, whl_files))
    batch = config.getint('DEFAULT', 'batch') or 20
    result = []
    start = 0
    end = batch
    batch_dep_version_files = dep_version_list[start:end]
    while len(batch_dep_version_files) > 0:
        check_result = batch_check_dependencies_by_safety(batch_dep_version_files)
        if len(check_result) !=0:
            result += check_result
        start = end
        end += batch
        batch_dep_version_files = dep_version_list[start:end]
    return result

def save_report(json_object):
    content = json.dumps(json_object, indent=2)
    today = date.today().strftime('%Y-%m-%d')
    file = os.path.join(report_path, config.get('DEFAULT', 'report_name').format(date=today))
    with open(file, 'w') as f:
        f.write(content)

def get_last_job_date():
    find_stream = os.popen('find {} -name "*.json"'.format(report_path))
    files = find_stream.read().strip().split('\n')
    file_names = list(map(lambda file: file.split(os.sep)[-1], files))
    file_dates = list(map(lambda file_name: re.search(r"^(.*)_safety.json", file_name).group(1), file_names))
    file_dates.sort(reverse=True)
    return file_dates[0]
    # find latest