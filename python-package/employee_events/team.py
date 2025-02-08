# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import dependencies for SQL execution
from employee_events.sql_execution import QueryMixin
import pandas as pd

# Create a subclass of QueryBase called `Team`
class Team(QueryBase):
    # Set the class attribute `name` to the string "team"
    name = "team"

    # Define a `names` method that receives no arguments
    # This method should return a list of tuples from an SQL execution
    def names(self):
        # Query 5: Retrieve all team names and IDs
        query = """
            SELECT team_name, team_id FROM team;
        """
        return self.query(query)

    # Define a `username` method that receives an ID argument
    # This method should return a list of tuples from an SQL execution
    def username(self, id):
        # Query 6: Retrieve a specific team name based on ID
        query = f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id};
        """
        return self.query(query)

    # Define a `model_data` method for machine learning model predictions
    def model_data(self, id):
        query = f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id,
                           SUM(positive_events) AS positive_events,
                           SUM(negative_events) AS negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                    GROUP BY employee_id
                   )
        """
        return self.pandas_query(query)
