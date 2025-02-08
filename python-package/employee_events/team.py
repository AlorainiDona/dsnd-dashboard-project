# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import dependencies for sql execution
# YOUR CODE HERE


# Create a subclass of QueryBase
# called  `Team`
class Team(QueryBase):

    # Set the class attribute `name`
    # to the string "team"
    name = "team"

    # Define a `names` method
    # that receives not arguments
    # This method should return
    # a list of tuples from ana sql execution
    def names(self):

        # Query 5
        # Write an SQL query that selects
        # the team_name and team_id columns
        # from the team table
        query = """
        SELECT team_id, team_name
         FROM team
        """
        return self.run_query(query)

    # Define a `username` method
    # that receives an id argument
    # This method should return
    # a list of tuples from an sql execution
    def username(self, id: int):
        # Query 6
        # Write an SQL query
        # that selects the team_name column
        # Use f-string formatting and a WHERE filter
        # to only return the team name for
        # the id argument
        query = f"""
            SELECT team_name
                FROM team
                WHERE team_id = {id}
        """
        return self.run_query(query)

    # YOUR CODE HERE
    # Below is method with an SQL query
    # This SQL query generates the data needed for
    # the machine learning model.
    # Without editing the query, alter this method
    # so when it is called, a pandas dataframe
    # is returns containing the execution of
    # the sql query
    def model_data(self, id):

        query = f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                    GROUP BY employee_id
                   )
                """
        return self.run_query_df(query)