from fasthtml.common import H1, RedirectResponse, Div
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

# Import the load_model function from the utils.py file
from utils import load_model

# Import base and combined components
from base_components import Dropdown, BaseComponent, Radio, MatplotlibViz, DataTable
from combined_components import FormGroup, CombinedComponent

# Initialize FastAPI app
app = FastAPI()

# Create a subclass of base_components/Dropdown
class ReportDropdown(Dropdown):
    def build_component(self, entity_id, model):
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()

# Create a subclass of base_components/BaseComponent
class Header(BaseComponent):
    def build_component(self, entity_id, model):
        return H1(model.name)

# Create a subclass of base_components/MatplotlibViz
class LineChart(MatplotlibViz):
    def visualization(self, entity_id, model):
        data = model.event_counts(entity_id)

        if data.empty:
            print("WARNING: No event data available.")
            return plt.figure()

        if "event_date" in data.columns:
            data.rename(columns={"event_date": "date"}, inplace=True)

        if "date" not in data.columns:
            print("ERROR: 'date' column is missing in the data!")
            return plt.figure()

        data.set_index("date", inplace=True)
        data.sort_index(inplace=True)
        data = data.cumsum()

        # Ensure at least two columns exist
        if data.shape[1] >= 2:
            data.columns = ["Positive", "Negative"]
        else:
            print("WARNING: Not enough columns for event trends visualization!")
            return plt.figure()

        fig, ax = plt.subplots()
        data.plot(ax=ax)
        self.set_axis_styling(ax)
        ax.set_title("Event Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("Count")
        return fig

# Create a subclass of base_components/MatplotlibViz
class BarChart(MatplotlibViz):
    predictor = load_model()

    def visualization(self, entity_id, model):
        data = model.model_data(entity_id)

        if data.empty:
            print("WARNING: model_data is empty, returning blank plot.")
            return plt.figure()

        probas = self.predictor.predict_proba(data)
        pred = probas[:, 1].mean() if model.name == "team" else probas[0, 1]

        fig, ax = plt.subplots()
        ax.barh([""], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Predicted Recruitment Risk", fontsize=20)
        self.set_axis_styling(ax)
        return fig

# Create a subclass of combined_components/CombinedComponent
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')

# Create a subclass of base_components/DataTable
class NotesTable(DataTable):
    def component_data(self, entity_id, model):
        return model.notes(entity_id)

class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector"
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]

# Create a subclass of CombinedComponents
class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]
    outer_div_type = Div(cls="container")

# Initialize the `Report` class
report = Report()

# Create routes that explicitly return HTMLResponse
@app.get("/", response_class=HTMLResponse)
def index():
    content = report(1, Employee())
    return HTMLResponse(content=content, status_code=200)

@app.get("/employee/{employee_id}", response_class=HTMLResponse)
def employee(employee_id: str):
    content = report(employee_id, Employee())
    return HTMLResponse(content=content, status_code=200)

@app.get("/team/{team_id}", response_class=HTMLResponse)
def team(team_id: str):
    content = report(team_id, Team())
    return HTMLResponse(content=content, status_code=200)

@app.get("/update_dropdown")
def update_dropdown(profile_type: str):
    dropdown = DashboardFilters.children[1]
    print("DEBUG: update_dropdown called with profile_type =", profile_type)

    if profile_type == "Team":
        return dropdown(None, Team())
    elif profile_type == "Employee":
        return dropdown(None, Employee())

@app.post("/update_data")
async def update_data(r):
    data = await r.form()
    profile_type = data.get("profile_type", "")
    entity_id = data.get("user-selection", "")

    if profile_type == "Employee":
        return RedirectResponse(f"/employee/{entity_id}", status_code=303)
    elif profile_type == "Team":
        return RedirectResponse(f"/team/{entity_id}", status_code=303)

# Start FastAPI server
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
