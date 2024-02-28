import argparse
import os
import subprocess
import sys
from datetime import datetime

import MySQLdb
import requests

EXPORT_CHECK_ENDPOINT = 'https://www.worldcubeassociation.org/api/v0/export/public'
TIMESTAMP_FILE = 'timestamp'
DATA_DIRECTORY = 'data'
MYSQL_DATABASE = 'wca'


def get_saved_timestamp() -> str | None:
    try:
        with open(TIMESTAMP_FILE) as f:
            return datetime.fromisoformat(f.readline().strip())
    except:
        return None


def update_timestamp(timestamp: datetime) -> None:
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(timestamp.isoformat())


def pull_newest_export(endpoint: str) -> str:
    '''
    Pulls the latest database export, unzipping the files into DATA_DIRECTORY.
    Returns the relative path of the SQL file pulled.
    '''
    zipfile = endpoint.split('/')[-1]

    subprocess.run(['curl', '-LO', endpoint]).check_returncode()
    subprocess.run(['rm', '-rf', DATA_DIRECTORY]).check_returncode()
    subprocess.run(['mkdir', '-p', DATA_DIRECTORY]).check_returncode()
    subprocess.run(['unzip', '-d', DATA_DIRECTORY, zipfile]).check_returncode()
    subprocess.run(['rm', zipfile]).check_returncode()

    return os.path.join(DATA_DIRECTORY, zipfile.removesuffix('.zip'))


def start_mysql() -> None:
    try:
        # Check if the server is already running
        db = MySQLdb.connect()
        db.close()
    except:
        subprocess.run(['mysql.server', 'start']).check_returncode()


def load_sql_export(sql_file: str) -> None:
    start_mysql()

    with MySQLdb.connect() as db:
        with db.cursor() as c:
            # Ensure the database exists and use it
            c.execute(f'create database if not exists {MYSQL_DATABASE}')
            c.execute(f'use {MYSQL_DATABASE}')

        # Load the export - the dump is so big that we need to use the command line
        print(f'Loading {sql_file} to database {MYSQL_DATABASE}...')

        with open(sql_file) as sql:
            subprocess.run(['mysql', MYSQL_DATABASE], stdin=sql).check_returncode()


def main() -> None:
    r = requests.get(EXPORT_CHECK_ENDPOINT)
    data = r.json()

    # Check for a saved export
    export_date = datetime.fromisoformat(data['export_date'])
    timestamp = get_saved_timestamp()

    if timestamp and timestamp >= export_date:
        print('Database up to date!')
        sys.exit()

    # Pull a new one if the current one is absent or outdated
    print(f'Current database export ({timestamp}) is out of date.'
          if timestamp else 'No database export found.')
    print(f'Pulling newest export ({export_date})...')

    sql_file = pull_newest_export(data['sql_url'])

    # Import it to MySQL
    load_sql_export(sql_file)

    # If nothing went wrong, we can finally update the timestamp
    update_timestamp(export_date)


if __name__ == '__main__':
    main()
