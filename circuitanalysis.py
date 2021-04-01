import numpy as np

class Circuit:
    def __init__(self, components, nodes):
        self.components = components
        self.nodes = nodes


    def detect_loops(self):
        pass


    def determine_parallel_connections(self):
        for component in self.components.values():
            node_1 = component.t1.wire.node
            node_2 = component.t2.wire.node
            for c in self.components.values():
                if c is not component:
                    if c not in component.parallel_connections:
                        n_1 = c.t1.wire.node
                        n_2 = c.t2.wire.node
                        if node_1 is n_1 and node_2 is n_2:
                            component.make_parallel_connection(c)


    def determine_series_connections(self):
        for node in self.nodes:
            components = node.components.copy()
            if len(components) == 2:
                c1, c2 = components.pop(), components.pop()
                c1.make_series_connection(c2)
                c2.make_series_connection(c1)

    def ohms_law(self):
        pass

    def kvl(self):
        pass

    def kcl(self):
        pass
