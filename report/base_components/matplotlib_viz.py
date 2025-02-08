from .base_component import BaseComponent
from fh_matplotlib import matplotlib2fasthtml


class MatplotlibViz(BaseComponent):

    @matplotlib2fasthtml
    def build_component(self, entity_id, model):
        return self.visualization(entity_id, model)

    def visualization(self, entity_id, model):
        pass