
from .query_base import QueryBase
from .sql_execution import QueryMixin
import pandas as pd


class Team(QueryBase, QueryMixin):
    """
    A class for querying team-related data.

    Attributes:
    ----------
    name : str
        The table name associated with teams.
    """

    name = "team"

    def names(self):
        """
        Retrieves a list of all teams with their names and IDs.

        SQL Query:
        ----------
        SELECT team_name, team_id
        FROM team;

        Returns:
        -------
        list[tuple]
            A list of tuples where each tuple contains:
            - Team name (str)
            - Team ID (int)
        """
        sql_query = """
            SELECT 
                team_name, 
                team_id
            FROM team;
        """
        return self.query(sql_query)

    def username(self, id):
        """
        Retrieves the name of a team by its ID.

        SQL Query:
        ----------
        SELECT team_name
        FROM team
        WHERE team_id = ?;

        Parameters:
        ----------
        id : int
            The team's ID.

        Returns:
        -------
        list[tuple]
            A list containing a single tuple with the team name.
        """
        if not isinstance(id, int):
            raise ValueError(f"Expected an integer for ID, but got {type(id).__name__}")

        sql_query = """
            SELECT 
                team_name
            FROM team
            WHERE team_id = ?;
        """
        return self.query(sql_query, [id])

    def model_data(self, id):
        """
        Retrieves model data for a given team.

        SQL Query:
        ----------
        SELECT positive_events, negative_events
        FROM (
            SELECT employee_id,
                   SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM team
            JOIN employee_events
            USING(team_id)
            WHERE team.team_id = ?
            GROUP BY employee_id
        );

        Parameters:
        ----------
        id : int
            The team's ID.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing:
            - Positive events count
            - Negative events count
        """
        if not isinstance(id, int):
            raise ValueError(f"Expected an integer for ID, but got {type(id).__name__}")

        sql_query = """
            SELECT 
                positive_events, 
                negative_events 
            FROM (
                SELECT 
                    employee_id,
                    SUM(positive_events) AS positive_events,
                    SUM(negative_events) AS negative_events
                FROM team
                JOIN employee_events
                USING(team_id)
                WHERE team.team_id = ?
                GROUP BY employee_id
            );
        """
        return self.pandas_query(sql_query, [id])
