import pandas as pd
from .sql_execution import QueryMixin

class QueryBase(QueryMixin):
    """
    Base class for executing SQL queries related to employee or team data.

    Attributes:
    ----------
    name : str
        Name of the table associated with the query.
    db_path : str
        Path to the SQLite database.
    """

    name = ""

    @staticmethod
    def names() -> list:
        """
        Returns a list of names associated with the class.

        Returns:
        -------
        list
            An empty list as the default implementation.
        """
        return []

    def event_counts(self, id: int) -> pd.DataFrame:
        """
        Retrieves the total positive and negative events grouped by date for a specific ID.

        Parameters:
        ----------
        id : int
            The unique identifier for the employee or team.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing `event_date`, `total_positive_events`, and `total_negative_events`.
            Returns an empty DataFrame if no data is found.
        """
        table_column = f"{self.name}_id"  # Dynamically determine the column (employee_id or team_id)
        sql_query = f"""
        SELECT event_date,
            SUM(positive_events) AS total_positive_events,
            SUM(negative_events) AS total_negative_events
        FROM employee_events
        WHERE {table_column} = ?
        GROUP BY event_date
        ORDER BY event_date;
        """
        df = self.pandas_query(sql_query, [id])
        if df.empty:
            return pd.DataFrame(columns=["event_date", "total_positive_events", "total_negative_events"])
        return df


    def notes(self, id: int) -> pd.DataFrame:
        """
        Retrieves notes associated with a specific ID, ordered by date.

        Parameters:
        ----------
        id : int
            The unique identifier for the employee or team.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing `note_date` and `note`.
            Returns an empty DataFrame if no data is found.
        """
        sql_query = f"""
        SELECT note_date, note
        FROM notes
        WHERE {self.name}_id = ?
        ORDER BY note_date;
        """
        df = self.pandas_query(sql_query, [id])
        if df.empty:
            return pd.DataFrame(columns=["note_date", "note"])
        return df