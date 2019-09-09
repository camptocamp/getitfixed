import time
from sqlalchemy.sql import text


def wait_for_db(connection):
    sleep_time = 1
    max_sleep = 30
    while sleep_time < max_sleep:
        try:
            connection.execute(text("SELECT 1;"))
            return
        except Exception as e:
            print(str(e))
            print("Waiting for the DataBase server to be reachable")
            time.sleep(sleep_time)
            sleep_time *= 2
    exit(1)
