import pytest
from pathlib import Path

# Using pathlib, create a project_root
# variable set to the absolute path for the root of this project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Apply the pytest fixture decorator to a `db_path` function
@pytest.fixture
def db_path():
    """Returns the absolute path to the SQLite database file"""
    return PROJECT_ROOT / "python-package" / "employee_events" / "employee_events.db"

# Define a function called `test_db_exists`
# This function should receive an argument
# with the same name as the function that creates the "fixture" for
# the database's filepath
def test_db_exists(db_path):
    """Test if the SQLite database file exists"""
    assert db_path.is_file()

# Apply pytest fixture to establish a database connection
@pytest.fixture
def db_conn(db_path):
    """Creates a connection to the SQLite database"""
    from sqlite3 import connect
    return connect(db_path)

# Fixture to retrieve all table names
@pytest.fixture
def table_names(db_conn):
    """Returns a list of all table names in the database"""
    name_tuples = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return [x[0] for x in name_tuples]

# Define a test function called `test_employee_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_employee_table_exists(table_names):
    """Test if the 'employee' table exists in the database"""
    assert "employee" in table_names

# Define a test function called `test_team_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_team_table_exists(table_names):
    """Test if the 'team' table exists in the database"""
    assert "team" in table_names

# Define a test function called `test_employee_events_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_employee_events_table_exists(table_names):
    """Test if the 'employee_events' table exists in the database"""
    assert "employee_events" in table_names
