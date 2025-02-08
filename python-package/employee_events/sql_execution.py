from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Using pathlib, create a `db_path` variable
# that points to the absolute path for the `employee_events.db` file
# YOUR CODE HERE
db_path = Path(__file__).parent / 'employee_events.db'


class QueryMixin:

    def run_query(self, query_string):
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    # Returns a pandas dataframe
    def run_query_df(self, query_string):
        connection = connect(db_path)
        df = pd.read_sql(query_string, connection)
        connection.close()
        return df


def query(func):

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query