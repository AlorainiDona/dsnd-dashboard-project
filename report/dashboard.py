
from fasthtml.common import *
import matplotlib.pyplot as plt
from fastapi import FastAPI, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)
TEMPLATES_DIR = os.path.join(BASE_DIR, "report", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "report", "static")
from python-package.employee_events import Employee, Team

from utils import load_model
import pandas as pd

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


class ReportDropdown(Dropdown):
    """
    A dropdown component for selecting an entity.

    Methods:
        build_component(entity_id, model):
            Builds the dropdown HTML based on the provided entity and model.
        component_data(entity_id, model):
            Fetches the data required to populate the dropdown options.
    """

    def build_component(self, entity_id, model):
        """
        Build the HTML for the dropdown selector.

        Args:
            entity_id (int): The ID of the selected entity.
            model (object): The model (Employee or Team) providing dropdown data.

        Returns:
            str: The HTML string for the dropdown selector.

        Raises:
            ValueError: If model or entity_id is None.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if type(model) == int:  # Handle swapped parameters
            model, entity_id = entity_id, model
        
        self.label = model.name
        options_html = "".join(
            f'<option value="{item["value"]}">{item["label"]}</option>' 
            for item in self.component_data(entity_id, model)
        )
        return f"""
        <label for="entity-selector">Select {model.name.capitalize()}:</label>
        <select id="entity-selector" name="entity">
            {options_html}
        </select>
        """

    def component_data(self, entity_id, model):
        """
        Fetch the data required to populate the dropdown.

        Args:
            entity_id (int): The ID of the selected entity.
            model (object): The model (Employee or Team) providing dropdown data.

        Returns:
            list: A list of dictionaries containing 'value' and 'label' for dropdown options.

        Raises:
            ValueError: If model or entity_id is None.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if type(model) == int:  # Handle swapped parameters
            model, entity_id = entity_id, model
        
        return model.names()


class Header(BaseComponent):
    """
    A component for generating a dynamic report header.

    Methods:
        build_component(entity_id, model):
            Builds the header HTML for the report.
    """

    def build_component(self, entity_id, model):
        """
        Build the HTML for the report header.

        Args:
            entity_id (int): The ID of the entity (Employee or Team).
            model (object): The model (Employee or Team) associated with the entity.

        Returns:
            str: The HTML string for the report header.

        Raises:
            ValueError: If model or entity_id is None.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if type(model) == int:  # Handle swapped parameters
            model, entity_id = entity_id, model
        
        # Determine correct possessive form of the name
        username = model.username(entity_id)[0][0]
        possessive = f"{username}'s" if not username.endswith("s") else f"{username}'"
        
        # Return header string
        return f"<h1>{possessive} {model.name.capitalize() if isinstance(model, Employee) else ''} Report</h1>"

class LineChart(MatplotlibViz):
    """
    A class for generating line charts visualizing cumulative events over time.

    Methods:
        visualization(model, entity_id):
            Prepares and saves a line chart based on the provided model and entity ID.
    """

    def visualization(self, model, entity_id):
        """
        Generate and save a line chart for cumulative events over time.

        Args:
            model (object): The model (Employee or Team) providing event data.
            entity_id (int): The ID of the entity whose events are visualized.

        Returns:
            str: Relative file path to the saved chart, or a message indicating no data is available.

        Raises:
            ValueError: If model or entity_id is None.

        Debugging:
            Prints critical paths and status during chart generation to facilitate troubleshooting.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if type(model) == int:  # Handle swapped parameters
            model, entity_id = entity_id, model

        print(f"Generating LineChart for entity_id: {entity_id}, model: {model.name}")
        
        # Prepare data
        data = model.event_counts(entity_id)
        print(f"Event counts data for entity_id {entity_id}: {data}")
        if data.empty:
            print(f"No data available for entity_id: {entity_id}")
            return f"<p>No data available to generate Line Chart for {model.name} with ID {entity_id}.</p>"

        # Clean and process data
        data.fillna(0, inplace=True)
        data.set_index("event_date", inplace=True)
        data.sort_index(inplace=True)
        data = data.cumsum()
        data.columns = ["Positive", "Negative"]

        # Create chart
        fig, ax = plt.subplots()
        data.plot(ax=ax)
        ax.set_title(f"Cumulative Events Over Time ({model.username(entity_id)[0][0]})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Event Count")

        # Debug and save chart
        print(f"STATIC_DIR: {STATIC_DIR}")  # Verify STATIC_DIR
        print(f"Static directory path: {STATIC_DIR}")  # Check the static directory path
        print(f"Static directory exists: {os.path.exists(STATIC_DIR)}")  # Ensure the directory exists
        os.makedirs(STATIC_DIR, exist_ok=True)

        file_path = os.path.join(STATIC_DIR, f"line_chart_{entity_id}.png")
        print(f"Saving LineChart to {file_path}")
        try:
            fig.savefig(file_path)
            print(f"Chart successfully saved to: {file_path}")  # Confirm file saved
        except Exception as e:
            print(f"Error saving chart: {e}")  # Catch any errors

        plt.close(fig)
        return f"static/line_chart_{entity_id}.png"

class BarChart(MatplotlibViz):
    """
    A class for generating bar charts visualizing predicted recruitment risk.

    Attributes:
        predictor: The trained model used to predict probabilities for the bar chart.

    Methods:
        visualization(model, entity_id):
            Prepares and saves a bar chart based on the provided model and entity ID.
    """

    predictor = load_model()

    def visualization(self, model, entity_id):
        """
        Generate and save a bar chart for predicted recruitment risk.

        Args:
            model (object): The model (Employee or Team) providing data for the chart.
            entity_id (int): The ID of the entity being visualized.

        Returns:
            str: Relative file path to the saved chart, or a message indicating no data is available.

        Raises:
            ValueError: If model or entity_id is None.

        Debugging:
            Prints critical paths, predictions, and statuses during chart generation for troubleshooting.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if type(model) == int:  # Handle swapped parameters
            model, entity_id = entity_id, model

        print(f"Generating BarChart for entity_id: {entity_id}, model: {model.name}")
        
        # Prepare data
        data = model.model_data(entity_id)
        print(f"Model data for entity_id {entity_id}: {data}")
        if data.empty:
            print(f"No model data available for entity_id: {entity_id}")
            return f"<p>No data available to generate Bar Chart for {model.name} with ID {entity_id}.</p>"

        # Predict probabilities
        probabilities = self.predictor.predict_proba(data)[:, 1]
        pred = probabilities.mean() if model.name == "team" else probabilities[0]

        # Create chart
        fig, ax = plt.subplots()
        ax.barh([""], [pred], color="blue")
        ax.set_xlim(0, 1)
        ax.set_title(f"Predicted Recruitment Risk ({model.username(entity_id)[0][0]})", fontsize=20)

        # Debug and save chart
        print(f"STATIC_DIR: {STATIC_DIR}")  # Verify STATIC_DIR
        print(f"Static directory path: {STATIC_DIR}")  # Check the static directory path
        print(f"Static directory exists: {os.path.exists(STATIC_DIR)}")  # Ensure the directory exists
        os.makedirs(STATIC_DIR, exist_ok=True)

        file_path = os.path.join(STATIC_DIR, f"bar_chart_{entity_id}.png")
        print(f"Saving BarChart to {file_path}")
        try:
            fig.savefig(file_path)
            print(f"Chart successfully saved to: {file_path}")  # Confirm file saved
        except Exception as e:
            print(f"Error saving chart: {e}")  # Catch any errors

        plt.close(fig)
        return f"static/bar_chart_{entity_id}.png"

class Visualizations(CombinedComponent):
    """
    A class for rendering visualizations (LineChart and BarChart) for a specific entity and model.

    Methods:
        render(entity_id, model):
            Generates and returns HTML for visualizations (LineChart and BarChart).
    """

    def render(self, entity_id, model):
        """
        Render visualizations (LineChart and BarChart) for the given entity and model.

        Args:
            entity_id (int): The ID of the entity for which the visualizations are generated.
            model (object): The model (Employee or Team) providing data for the visualizations.

        Returns:
            str: An HTML string containing the visualizations or messages indicating their unavailability.

        Debugging:
            Logs critical steps, including chart generation attempts, validation, and final HTML creation.

        Error Handling:
            Catches and logs exceptions during the chart generation process to prevent crashes.
        """
        print(f"Visualizations.render() called for entity_id: {entity_id}, model: {model.name}")  # Debug start

        # Attempt to generate LineChart
        try:
            print(f"Calling LineChart.visualization() for entity_id: {entity_id}")  # Debug LineChart call
            line_chart_path = LineChart().visualization(model, entity_id)
            print(f"LineChart path returned: {line_chart_path}")  # Debug LineChart result
        except Exception as e:
            print(f"Error generating LineChart: {e}")  # Catch any errors
            line_chart_path = None

        # Attempt to generate BarChart
        try:
            print(f"Calling BarChart.visualization() for entity_id: {entity_id}")  # Debug BarChart call
            bar_chart_path = BarChart().visualization(model, entity_id)
            print(f"BarChart path returned: {bar_chart_path}")  # Debug BarChart result
        except Exception as e:
            print(f"Error generating BarChart: {e}")  # Catch any errors
            bar_chart_path = None

        # Validate LineChart
        if not line_chart_path:
            print(f"LineChart not generated or returned None for entity_id: {entity_id}")  # Debug validation
            line_chart_html = "<p>Line Chart not available.</p>"
        else:
            line_chart_html = f'<img src="/{line_chart_path}" alt="Line Chart" />'

        # Validate BarChart
        if not bar_chart_path:
            print(f"BarChart not generated or returned None for entity_id: {entity_id}")  # Debug validation
            bar_chart_html = "<p>Bar Chart not available.</p>"
        else:
            bar_chart_html = f'<img src="/{bar_chart_path}" alt="Bar Chart" />'

        # Debug the final HTML generation
        final_html = f"""
        <div class="visualizations">
            {line_chart_html}
            {bar_chart_html}
        </div>
        """
        print(f"Final HTML generated for Visualizations: {final_html}")  # Debug final output

        return final_html

class NotesTable(DataTable):
    """
    A class for rendering a notes table component for a specific entity and model.

    Methods:
        component_data(entity_id, model):
            Fetches and validates notes data as a pandas DataFrame.
        build_component(entity_id, model):
            Builds and returns the HTML representation of the notes table.
    """

    def component_data(self, entity_id, model):
        """
        Fetch and validate data for the notes table.

        Args:
            entity_id (int): The ID of the entity for which the notes are fetched.
            model (object): The model providing notes data.

        Returns:
            pandas.DataFrame: A DataFrame containing the notes data.

        Raises:
            ValueError: If `model` or `entity_id` is None.
            TypeError: If the returned data is not a pandas DataFrame.

        Ensures:
            The returned DataFrame is valid and suitable for rendering.
        """
        if model is None or entity_id is None:
            raise ValueError("Model or entity_id is None. Please check the inputs.")
        if isinstance(model, int):
            model, entity_id = entity_id, model

        # Fetch notes data
        df = model.notes(entity_id)
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame from model.notes().")
        return df

    def build_component(self, entity_id, model):
        """
        Build the HTML representation of the notes table.

        Args:
            entity_id (int): The ID of the entity for which the notes table is built.
            model (object): The model providing notes data.

        Returns:
            str: An HTML string representing the notes table.

        Raises:
            ValueError: If the DataFrame is missing required columns.

        Process:
            - Fetch and validate the notes data.
            - Convert DataFrame rows into HTML table rows.
            - Wrap the rows in a complete HTML table structure.
        """
        # Fetch and validate notes data
        df = self.component_data(entity_id, model)

        # Validate required columns
        required_columns = ["note_date", "note"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame is missing required columns: {', '.join(required_columns)}.")

        # Convert rows to HTML
        table_rows = "".join(
            f"<tr><td>{row['note_date']}</td><td>{row['note']}</td></tr>"
            for _, row in df.iterrows()
        )

        # Build HTML table
        return f"""
        <table class="notes-table">
            <thead>
                <tr>
                    <th>Note Date</th>
                    <th>Note</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """

class DashboardFilters(FormGroup):
    """
    A class for rendering and managing dashboard filters, including radio buttons for
    profile type selection and a dynamically updating entity dropdown.

    Attributes:
        id (str): The HTML ID of the form.
        action (str): The URL to which the form data is submitted.
        method (str): The HTTP method for the form submission (default: POST).
        button_label (str): The label displayed on the form's submit button.
        profile_type_selector (Radio): A Radio component for selecting the profile type.
        entity_selector (Div): A Div component wrapping the dropdown selector for entities.
        children (list): A list of child components for the form.
    """

    id = "dashboard-filters-form"
    action = "/update_data"
    method = "POST"
    button_label = "Submit"

    def __init__(self):
        """
        Initialize the DashboardFilters component with default profile type and empty entity dropdown.
        """
        # Initialize the Radio component
        self.profile_type_selector = Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#entity-selector",
            selected="Employee",  # Default selection
        )

        # Define the entity dropdown with an empty set of options
        self.entity_selector = Div(
            Label("Select Entity:"),
            Select(id="entity", name="entity", options=[]),
        )

        # Add child components to the form
        self.children = [self.profile_type_selector, self.entity_selector]

    def render_radio(self):
        """
        Render the radio button group as HTML.

        Returns:
            str: An HTML string representing the radio button group.

        Note:
            A dummy model is passed to the `build_component` method to generate the radio buttons.
        """
        # Pass a dummy model with a name attribute
        dummy_model = type("DummyModel", (object,), {"name": "Employee"})()
        radio_components = self.profile_type_selector.build_component(None, dummy_model)
        return Div(*radio_components)  # Wrap the components in a Div container

    def render_dropdown(self, userid=None, model=None):
        """
        Render the entity dropdown as HTML.

        Args:
            userid (int, optional): The user ID interacting with the dashboard.
            model (object, optional): The model (Employee or Team) providing entity data.

        Returns:
            str: An HTML string representing the dropdown selector.

        Notes:
            - If a model is provided, the dropdown is populated with its entities.
            - If no model is provided, an empty dropdown is returned.
        """
        if model:
            # Build HTML options from the model's entities
            options_html = "".join(
                f'<option value="{entity[1]}">{entity[0]}</option>' for entity in model.names()
            )
            return f'<select id="entity" name="entity">{options_html}</select>'
        # Default empty dropdown
        return '<select id="entity" name="entity"><option value="">-- Select an Entity --</option></select>'

    def render(self, userid=None, model=None):
        """
        Render the complete filters form as HTML.

        Args:
            userid (int, optional): The user ID interacting with the dashboard.
            model (object, optional): The model (Employee or Team) providing entity data.

        Returns:
            str: An HTML string representing the full filters form.
        """
        radio_html = self.render_radio()
        dropdown_html = self.render_dropdown(userid, model)
        return f"""
        <form id="{self.id}" action="{self.action}" method="{self.method}" enctype="multipart/form-data">
            <fieldset>
                {radio_html}
                <div id="entity-selector">
                    {dropdown_html}
                </div>
                <button type="submit">{self.button_label}</button>
            </fieldset>
        </form>
        """

    def call_children(self, userid, model):
        """
        Dynamically update the child components, specifically the entity dropdown.

        Args:
            userid (int): The ID of the user interacting with the dashboard.
            model (object): The model (Employee or Team) providing entity data.

        Returns:
            list: A list of child components with the updated dropdown.

        Notes:
            - Updates the dropdown options dynamically based on the selected model.
            - Ensures the dropdown reflects the entities provided by the model.
        """
        # Call the parent method to initialize children
        children = super().call_children(userid, model)

        # Update the entity dropdown based on the model
        if model:
            options = [{"value": entity[1], "label": f"{entity[0]}"} for entity in model.names()]
            entity_dropdown = Select(id="entity", name="entity", options=options)
            self.entity_selector = Div(Label("Select Entity:"), entity_dropdown)
            children[1] = self.entity_selector  # Replace the second child with the updated dropdown

        return children

class Report:
    """
    A class responsible for rendering the report page with all its components,
    including the header, filters, visualizations, and notes table.

    Attributes:
        header (Header): Component to build the report header.
        filters (DashboardFilters): Component to manage and render dashboard filters.
        visualizations (Visualizations): Component to generate visualizations.
        notes_table (NotesTable): Component to build and display the notes table.
    """

    def __init__(self):
        """
        Initializes the Report class with all its components.
        """
        print("Initializing Report class")
        self.header = Header()
        self.filters = DashboardFilters()
        self.visualizations = Visualizations()
        self.notes_table = NotesTable()

    def render(self, request: Request, entity_id, model):
        """
        Render the report page using the `report_page.html` template.

        Args:
            request (Request): The incoming HTTP request object.
            entity_id (int): The ID of the entity (employee or team) to render the report for.
            model (object): The model (Employee or Team) providing data for the report.

        Returns:
            TemplateResponse: A rendered HTML response with all components of the report page.

        Notes:
            - The `DashboardFilters` component renders dynamic filters.
            - The header, visualizations, and notes table are generated based on the entity and model.
        """
        print(f"Rendering report for entity_id: {entity_id}, model: {model.name}")

        # Generate individual report components
        header_html = self.header.build_component(entity_id, model)
        visualizations_html = self.visualizations.render(entity_id, model)
        notes_html = self.notes_table.build_component(entity_id, model)

        # Render dropdown for dashboard filters
        rendered_dropdown = self.filters.render_dropdown(entity_id, model)

        # Determine the profile type and corresponding model for rendering
        render_model, profile_type = (
            (Employee(), "employee") if isinstance(model, Employee) else (Team(), "team")
        )

        # Return the rendered HTML page
        return templates.TemplateResponse(
            "report_page.html",
            {
                "request": request,
                "dashboard_filters": self.filters,  # Filters for rendering radio and dropdown
                "model": render_model,  # Rendered model for dropdown selection
                "entity_id": entity_id,  # ID of the selected entity
                "profile_type": profile_type,  # Profile type ("employee" or "team")
                "header_html": header_html,  # Rendered header component
                "visualizations_html": visualizations_html,  # Rendered visualizations
                "notes_html": notes_html,  # Rendered notes table
                "dropdown": rendered_dropdown,  # Dropdown rendered by DashboardFilters
                "model": model,  # Original model passed in (for context)
            },
        )

# Initialize a FastAPI application
app = FastAPI()

# Import required modules for static file handling and template rendering
from fastapi.staticfiles import StaticFiles  # Serve static files like CSS, JS, and images
from fastapi.templating import Jinja2Templates  # Render HTML templates using Jinja2

# Configure the directory for Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Mount the `/static` route for serving static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Landing Page Route
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """
    Render the landing page with default options for entity selection.

    Args:
        request (Request): The FastAPI request object used to handle the HTTP request.

    Returns:
        TemplateResponse: Renders the `landing_page.html` template populated with the default context.

    Purpose:
        - Provides the initial user interface to select a profile type (Employee or Team) and view a corresponding dropdown.
        - Acts as the entry point for the dashboard application, setting up the default state for the filters.

    Workflow:
        1. Instantiate the `DashboardFilters` class to generate filter options.
        2. Use the `Employee` model as the default selection for the dropdown.
        3. Generate the dropdown HTML by rendering the default model's entities.
        4. Render the `landing_page.html` template with all necessary data for the user interface.

    Example Usage:
        - Accessing `/` in the browser will load the landing page with Employee profile type and dropdown by default.
    """
    # Initialize DashboardFilters for rendering radio buttons and dropdown
    dashboard_filters = DashboardFilters()

    # Use Employee model as the default profile type and fetch dropdown options
    default_model = Employee()
    rendered_dropdown = dashboard_filters.render_dropdown(None, default_model)

    # Return the rendered landing page template
    return templates.TemplateResponse(
        "landing_page.html",
        {
            "request": request,  # Pass the request object for template rendering
            "dashboard_filters": dashboard_filters,  # Pass the filters object for rendering
            "default_model": default_model,  # Set the default profile type to Employee
            "default_dropdown": rendered_dropdown,  # Rendered dropdown for the Employee model
        },
    )

# Route to Employee Report
@app.get("/employee/{id:int}", response_class=HTMLResponse)
def employee_dashboard(request: Request, id: int):
    """
    Render the employee dashboard for a specific employee ID.

    Args:
        request (Request): The FastAPI request object.
        id (int): The unique ID of the employee to generate the report for.

    Returns:
        TemplateResponse: The rendered HTML page displaying the employee's dashboard report.

    Purpose:
        - Fetch data and visualizations for the given employee.
        - Display the employee-specific report in a structured format.

    Workflow:
        1. Instantiate the `Report` class to generate the required components.
        2. Pass the `Employee` model with the given ID to the `render` method.
        3. Return the fully rendered report as a `TemplateResponse`.

    Example Usage:
        - Access `/employee/2` to view the report for the employee with ID 2.
    """
    print(f"Accessing employee dashboard for ID: {id}")
    report = Report()
    return report.render(request, id, Employee())


# Route to Team Report
@app.get("/team/{id:int}", response_class=HTMLResponse)
def team_dashboard(request: Request, id: int):
    """
    Render the team dashboard for a specific team ID.

    Args:
        request (Request): The FastAPI request object.
        id (int): The unique ID of the team to generate the report for.

    Returns:
        TemplateResponse: The rendered HTML page displaying the team's dashboard report.

    Purpose:
        - Fetch data and visualizations for the given team.
        - Display the team-specific report in a structured format.

    Workflow:
        1. Instantiate the `Report` class to generate the required components.
        2. Pass the `Team` model with the given ID to the `render` method.
        3. Return the fully rendered report as a `TemplateResponse`.

    Example Usage:
        - Access `/team/3` to view the report for the team with ID 3.
    """
    print(f"Accessing team dashboard for ID: {id}")
    report = Report()
    return report.render(request, id, Team())

# Dropdown update route
@app.get('/update_dropdown')
def update_dropdown(profile_type: str = Query(...)):
    """
    Dynamically update the entity dropdown based on the selected profile type.

    Args:
        profile_type (str): The profile type selected by the user ("Employee" or "Team").

    Returns:
        HTMLResponse: Rendered HTML for the updated dropdown.
        dict: Error response with a 400 status code if the profile type is invalid.

    Purpose:
        - Handles the client-side request to update the dropdown dynamically when
          the user selects a different profile type.
        - Returns a dropdown populated with entities matching the selected profile type.

    Example Workflow:
        1. User selects "Employee" or "Team" on the UI.
        2. The frontend sends a GET request with the selected profile type.
        3. This route dynamically renders the appropriate dropdown.
    """
    dashboard_filters = DashboardFilters()
    if profile_type == 'Team':
        dropdown_html = dashboard_filters.render_dropdown(None, Team())
    elif profile_type == 'Employee':
        dropdown_html = dashboard_filters.render_dropdown(None, Employee())
    else:
        print("Invalid profile_type received.")
        return {"error": "Invalid profile type"}, 400

    return HTMLResponse(content=dropdown_html)


from fastapi import Form

# Update data route
@app.post('/update_data')
async def update_data(
    profile_type: str = Form(...),
    entity: str = Form(...)
):
    """
    Process form data and redirect based on the selected profile type and entity.

    Args:
        profile_type (str): The profile type selected by the user ("Employee" or "Team").
        entity (str): The selected entity ID from the dropdown.

    Returns:
        RedirectResponse: Redirects to the appropriate page (employee/team report).
        dict: Error response with a 400 status code if form data is invalid.

    Purpose:
        - Processes the form submission to determine which report page to load.
        - Redirects the user to the appropriate endpoint based on their selection.

    Example Workflow:
        1. User submits the form after selecting a profile type and entity.
        2. This route validates the inputs and redirects to `/employee/{entity}` or `/team/{entity}`.

    Example Usage:
        - Redirects to `/employee/2` if the user selected "Employee" and entity ID 2.
        - Redirects to `/team/5` if the user selected "Team" and entity ID 5.
    """
    if not profile_type or not entity:
        print("Missing form data")
        return {"error": "Missing profile_type or entity"}, 400

    if profile_type == 'Employee':
        print(f"Redirecting to /employee/{entity}")
        return RedirectResponse(f"/employee/{entity}", status_code=303)
    elif profile_type == 'Team':
        print(f"Redirecting to /team/{entity}")
        return RedirectResponse(f"/team/{entity}", status_code=303)
    else:
        print("Invalid profile_type received.")
        return {"error": "Invalid profile type"}, 400


# Serve the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
