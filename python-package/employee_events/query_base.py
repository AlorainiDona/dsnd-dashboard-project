# Import any dependencies needed to execute sql queries
# YOUR CODE HERE
from .sql_execution import QueryMixin
# Define a class called QueryBase



class QueryBase:
    name = ""
    # Create a class attribute called `name`
    # set the attribute to an empty string
    # YOUR CODE HERE

    # Define a `names` method that receives
    # no passed arguments
    # YOUR CODE HERE
    def names(self):
        return []
        # Return an empty list
        # YOUR CODE HERE


    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    # YOUR CODE HERE
    def event_counts(self, id):
        query = f"""
        SELECT event_date, 
               SUM(positive_events) as total_positive_events, 
               SUM(negative_events) as total_negative_events
        FROM employee_events
        WHERE {self.name}_id = {id}
        GROUP BY event_date
        ORDER BY event_date
        """
        return QueryMixin().pandas_query(query)
    

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    # YOUR CODE HERE
    def notes(self, id):
        query = f"""
        select note_date, note from notes
        where {self.name}_id = {id}
        """
        # QUERY 2
        # Write an SQL query that returns `note_date`, and `note`
        # from the `notes` table
        # Set the joined table names and id columns
        # with f-string formatting
        # so the query returns the notes
        # for the table name in the `name` class attribute
        return QueryMixin().pandas_query(query)