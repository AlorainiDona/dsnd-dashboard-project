# Import dependencies for SQL execution
from employee_events.sql_execution import QueryMixin

import pandas as pd

# Define a class called QueryBase
# Use inheritance to add methods for querying the database
class QueryBase(QueryMixin):

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ""

    # Define a `names` method that receives no arguments
    def names(self):
        """Returns an empty list (To be overridden by subclasses)"""
        return []

    # Define an `event_counts` method that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id):
        """Returns event counts grouped by date"""
        query = f"""
            SELECT event_date, 
                   SUM(positive_events) AS positive_events, 
                   SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date;
        """
        return self.pandas_query(query)

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id):
        """Returns notes for the given entity"""
        query = f"""
            SELECT note_date, note
            FROM notes
            JOIN {self.name}
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id};
        """
        return self.pandas_query(query)
