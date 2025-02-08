from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

db_path = Path(__file__).parent / "employee_events.db"

class QueryMixin:
    """
    A mixin class providing methods to execute SQL queries
    and retrieve results as pandas DataFrames or lists of tuples.
    """

    def pandas_query(self, sql_query: str, params: list = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns the result as a pandas DataFrame.

        Parameters:
        ----------
        sql_query : str
            The SQL query to execute.
        params : list, optional
            Parameters for the SQL query, default is None.

        Returns:
        -------
        pandas.DataFrame
            The query result as a DataFrame.
        """
        if params is None:
            params = []

        connection = connect(db_path)
        try:
            result = pd.read_sql_query(sql_query, connection, params=params)
        finally:
            connection.close()
        return result

    def query(self, sql_query: str, params: list = None) -> list[tuple]:
        """
        Executes a SQL query and returns the result as a list of tuples.

        Parameters:
        ----------
        sql_query : str
            The SQL query to execute.
        params : list, optional
            Parameters for the SQL query. Defaults to None.

        Returns:
        -------
        list[tuple]
            The query result as a list of tuples.
        """
        print(f"Executing SQL Query: {sql_query}")
        print(f"With Parameters: {params}")
        print(f"Using Database Path: {db_path}")

        connection = connect(db_path)
        cursor = connection.cursor()
        try:
            if params is not None:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
            result = cursor.fetchall()
            print(f"Query Result: {result}")
        finally:
            connection.close()
        return result

# Leave this code unchanged
def query(func):
    """
    Decorator that executes a SQL query and returns the result as a list of tuples.

    The decorated function should return a SQL query string.

    Returns:
    -------
    list[tuple]
        The query result as a list of tuples.
    """
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        try:
            result = cursor.execute(query_string).fetchall()
        finally:
            connection.close()
        return result

    return run_query