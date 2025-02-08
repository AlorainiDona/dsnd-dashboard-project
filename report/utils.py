import pickle
from pathlib import Path

# Using the Path object, create a `project_root` variable
# set to the absolute path for the root of this project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Using the `project_root` variable
# create a `model_path` variable
# that points to the file `model.pkl`
# inside the assets directory
MODEL_PATH = PROJECT_ROOT / "assets" / "model.pkl"

def load_model():
    with MODEL_PATH.open('rb') as file:
        model = pickle.load(file)
    return model
