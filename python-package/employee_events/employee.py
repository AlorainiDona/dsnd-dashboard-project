# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import dependencies needed for SQL execution
# from the `sql_execution` module
from employee_events.sql_execution import QueryMixin
import pandas as pd

# Define a subclass of QueryBase called Employee
class Employee(QueryBase):
    # Set the class attribute `name` to the string "employee"
    name = "employee"

    # Define a method called `names` that receives no arguments
    # This method should return a list of tuples from an SQL execution
    def names(self):
        # Query 3: Retrieve employees' full names and IDs
        query = """
            SELECT first_name || ' ' || last_name AS full_name, employee_id
            FROM employee;
        """
        return self.query(query)

    # Define a method called `username` that receives an `id` argument
    # This method should return a list of tuples from an SQL execution
    def username(self, id):
        # Query 4: Retrieve a specific employee's full name
        query = f"""
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = {id};
        """
        return self.query(query)

    # Define a method called `model_data` that retrieves
    # data for machine learning model predictions
    def model_data(self, id):
        query = f"""
            SELECT SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """
        return self.pandas_query(query)
