# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import dependencies needed for sql execution
# YOUR CODE HERE


# Define a subclass of QueryBase
# called Employee
class Employee(QueryBase):

    # Set the class attribute `name`
    # to "employee"
    name = "employee"

    # Define a method called `names`
    # that receives not arguments
    # This method should return a list of tuples
    # from an sql execution
    def names(self):
        # Query 3
        # Write an SQL query
        # that selects the full name and id for all employees
        query = """
                    SELECT employee_id,
                        first_name || ' ' || last_name as full_name
                        FROM employee
                """
        return self.run_query(query)

    # Define a method called `username`
    # that receives an `id` argument
    # This method should return a list of tuples
    # from an sql execution
    def username(self, id: int):
        # Query 4
        # Write an SQL query
        # that selects an employees full name
        # Use f-string formatting and a WHERE filter
        # to only return the full name of the employee
        # with an id equal to the id argument
        query = f"""
                SELECT first_name || ' ' || last_name as full_name
                    FROM employee
                    WHERE employee_id = {id}
                """
        return self.run_query_df(query)

    # Below is method with an SQL query
    # This SQL query generates the data needed for
    # the machine learning model.
    # Without editing the query, alter this method
    # so when it is called, a pandas dataframe
    # is returns containing the execution of
    # the sql query
    def model_data(self, id):

        query = f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                """
        return self.run_query_df(query)