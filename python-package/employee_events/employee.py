from .query_base import QueryBase
from .sql_execution import QueryMixin

class Employee(QueryBase, QueryMixin):
    """
    A class for querying employee-related data.

    Attributes:
    ----------
    name : str
        The table name associated with employees.
    """

    name = "employee"

    def names(self):
        """
        Retrieves a list of all employees with their full names and IDs.

        SQL Query:
        ----------
        SELECT first_name || ' ' || last_name AS full_name,
               employee_id
        FROM employee

        Returns:
        -------
        list[tuple]
            A list of tuples containing:
            - Full name (str)
            - Employee ID (int)
        """
        sql_query = """
            SELECT 
                first_name || ' ' || last_name AS full_name,
                employee_id
            FROM employee
        """
        return self.query(sql_query)

    def username(self, id):
        """
        Retrieves the full name of an employee by their ID.

        SQL Query:
        ----------
        SELECT first_name || ' ' || last_name AS full_name
        FROM employee
        WHERE employee_id = ?

        Parameters:
        ----------
        id : int
            The employee's ID.

        Returns:
        -------
        list[tuple]
            A list containing a single tuple with the full name of the employee.
        """
        if not isinstance(id, int):
            raise ValueError(f"Expected an integer for ID, but got {type(id).__name__}")

        sql_query = """
            SELECT 
                first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = ?
        """
        return self.query(sql_query, [id])

    def model_data(self, id):
        """
        Retrieves aggregated event data for a specific employee.

        SQL Query:
        ----------
        SELECT SUM(positive_events) AS positive_events,
               SUM(negative_events) AS negative_events
        FROM employee
        JOIN employee_events USING(employee_id)
        WHERE employee.employee_id = ?

        Parameters:
        ----------
        id : int
            The employee's ID.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing:
            - Sum of positive events
            - Sum of negative events
        """
        if not isinstance(id, int):
            raise ValueError(f"Expected an integer for ID, but got {type(id).__name__}")

        sql_query = """
            SELECT 
                SUM(positive_events) AS positive_events,
                SUM(negative_events) AS negative_events
            FROM employee
            JOIN employee_events
            USING(employee_id)
            WHERE employee.employee_id = ?
        """
        return self.pandas_query(sql_query, [id])