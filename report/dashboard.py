from fasthtml.common import *
import matplotlib.pyplot as plt
from fasthtml.common import App



# Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

# Import the load_model function from the utils.py file
from utils import load_model

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


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    def build_component(self, entity_id, model):
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):
    def build_component(self, entity_id, model):
        return H1(model.name)


# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    def visualization(self, entity_id, model):
        data = model.event_counts(entity_id)
        data.fillna(0, inplace=True)
        data.set_index("date", inplace=True)
        data.sort_index(inplace=True)
        data = data.cumsum()
        data.columns = ["Positive", "Negative"]
        fig, ax = plt.subplots()
        data.plot(ax=ax)
        self.set_axis_styling(ax, border_color="black", font_color="black")
        ax.set_title("Event Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("Count")
        return fig


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):
    predictor = load_model()

    def visualization(self, entity_id, model):
        data = model.model_data(entity_id)
        probas = self.predictor.predict_proba(data)
        pred = probas[:, 1].mean() if model.name == "team" else probas[0, 1]
        fig, ax = plt.subplots()
        ax.barh([""], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Predicted Recruitment Risk", fontsize=20)
        self.set_axis_styling(ax)
        return fig


# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')


# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):
    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    

# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]
    outer_div_type = Div(cls='container')


# Initialize a fasthtml app 
app = App()

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@app.get('/')
def index():
    return report(1, Employee())


# Create a route for a get request
@app.get('/employee/{employee_id}')
def employee(employee_id: str):
    return report(employee_id, Employee())


# Create a route for a get request
@app.get('/team/{team_id}')
def team(team_id: str):
    return report(team_id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    

serve()
