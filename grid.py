from component import *


class Point():
    def __init__(self, scr_coord, grid_coord):
        self.loc = scr_coord
        self.grid_loc = grid_coord
        self.restricted_for_components = False
        self.restricted_for_wires = False
        # if the point is part of a wire, it will be set equal to that wire
        self.wire = None
        self.node = None

    def __repr__(self):
        return 'Point object at grid coordinate {}'.format(self.grid_loc)
    
    def __str__(self):
        return str(self.grid_loc)

    def set_wire(self, wire):
        if self.wire is None:
            self.wire = wire
            self.restricted_for_components = True

    def set_node(self, node):
        self.node = node
    
    def default(self):
        self.restricted = False
        self.is_center_point = False
        self.wire = None
        self.node = None


class Grid():
    def __init__(self):
        self.pts = {}
        self.components = {}
        self.wires = []       # DO NOT MAKE THIS A SET; order matters because certain method pop the most recently added wire
        self.new_wire_stack = []
        self.new_components = set()
        self.track_stack = [] # contains a list of tuples; (wire, is_wire_valid)
        self.wire_pts = []
        self.nodes = set() 

    def default_grid(self):
        for pt in self.pts.values():
            pt.default()

        self.wires.clear()
        self.components.clear()
        self.nodes.clear()
        self.wire_pts.clear()
        self.nodes.clear()
        self.new_components.clear()

    # function should behave similarly to the add_wire() method
    # except it should not add to the wires list
    # it also should not call the wire's restrict_points() method
    # it should then return whether the wire is valid or not
    def add_temp_wire(self, s, e):
        s_g = s.grid_loc
        e_g = e.grid_loc

        orientation, direction = self.det_wire_orientation(s_g, e_g)

        if orientation and direction:
            temp_wire = Wire(s, e, self.pts, orientation, direction, is_temp_wire=True)
            is_temp_wire_valid = self.is_valid_wire(s, e)
            self.track_stack.append((temp_wire, is_temp_wire_valid))
        else:
            s_x = s_g[0]
            s_y = s_g[1]
            e_x = e_g[0]
            e_y = e_g[1]

            p1 = (s_x, e_y)
            p2 = (e_x, s_y)
            dis1 = math.dist(s.grid_loc, p1)
            dis2 = math.dist(s.grid_loc, p2)

            if dis1 <= dis2:
                self.add_temp_wire(s, self.pts[p1])
                self.add_temp_wire(self.pts[p1], e)
            else:
                self.add_temp_wire(s, self.pts[p2])
                self.add_temp_wire(self.pts[p2], e)

        return self.track_stack

    def check_new_wire_connection(self):
        for wire in self.new_wire_stack:
            for w in self.wires:
                if w != wire:
                    wire.make_connection(w.start_pt, w)
                    wire.make_connection(w.end_pt, w)
            for component in self.components.values():
                t1_pt = component.t1.pt
                t2_pt = component.t2.pt
                wire.make_connection(t1_pt, component.t1)
                wire.make_connection(t2_pt, component.t2)

    def check_new_component_connection(self, component):
        for w in self.wires:
            component.t1.make_connection(w.start_pt, w)
            component.t1.make_connection(w.end_pt, w)
            component.t2.make_connection(w.start_pt, w)
            component.t2.make_connection(w.end_pt, w)

    def update_nodes(self):
        nodes_wire_touches = []
        if self.nodes:
            for node in self.nodes:
                for wire in self.new_wire_stack:
                    for pt in wire.points:
                        if pt.wire in node.wires:
                            nodes_wire_touches.append(node)
            if not nodes_wire_touches:
                new_node = Node(self.new_wire_stack)
                self.nodes.add(new_node)
            elif len(nodes_wire_touches) == 1:
                node = nodes_wire_touches.pop(0)
                node.add_wire(self.new_wire_stack)
            else:
                merged_wires = []
                for n in nodes_wire_touches:
                    merged_wires += n.wires
                    self.nodes.remove(n)
                merged_wires += self.new_wire_stack
                merged_node = Node(merged_wires)
                self.nodes.add(merged_node)        
        else:
            new_node = Node(self.new_wire_stack)
            self.nodes.add(new_node)

    # TODO: maybe make a mesh class
    def identify_mesh(self):
        pass

    # TODO: determine if components in circuit are in series or in parallel
    #       two components are in parallel if they have matching nodes at each terminal
    #       two components are in series if they share at least one node where they are
    #       only components connected to that node
    def determine_connection_types(self):
        self.reset_connection_types()
        self.determine_parallel_connections()
        self.determine_series_connections()
        self.print_connection_types()

    # there are probably still bugs with this BUT IT WORKS MOSTLY
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


    def print_connection_types(self):
        for component in self.components.values():
            print("{} is parallel to {}".format(repr(component), component.parallel_connections))
            print("{} is in series with {}".format(repr(component), component.series_connections))
            print("\n \n")
        

    def reset_connection_types(self):
        for component in self.components.values():
            component.parallel_connections.clear()
            component.series_connections.clear()

    def is_complete_circuit(self):
        for component in self.components.values():
            if component.t1.wire is None or component.t2.wire is None:
                return False
        else:
            return True

    def print_all_nodes(self):
        print("NEW")
        for node in self.nodes:
            print(str(node))

    # calls add_wire() and then calls update_nodes()
    def add_wire_wrapper(self, s, e):
        self.add_wire(s, e)
        self.update_nodes()
        self.check_new_wire_connection()
        if self.is_complete_circuit():
            self.determine_connection_types()
        #self.print_all_nodes()

    # creates wire object and adds it to the logical grid
    # returns a false flag if the wire is invalid
    def add_wire(self, s, e):
        s_g = s.grid_loc
        e_g = e.grid_loc

        orientation, direction = self.det_wire_orientation(s_g, e_g)

        # if orientation and direction are not empty strings (s and e make a straight line)
        if orientation and direction:
            if self.is_valid_wire(s, e):
                new_wire = Wire(s, e, self.pts, orientation, direction)
                self.wires.append(new_wire)
                self.new_wire_stack.append(new_wire)
                return True

            else:
                # if the user placed a corner wire and the first half was valid but not the second half,
                # the first half needs to be removed from the wires list
                if self.new_wire_stack:
                    self.wires.pop(-1)
                    self.new_wire_stack.clear()
                return False

        # s and e are diagonal to one another, recursively create two wires
        else:
            s_x = s_g[0]
            s_y = s_g[1]
            e_x = e_g[0]
            e_y = e_g[1]

            p1 = (s_x, e_y)
            p2 = (e_x, s_y)
            dis1 = math.dist(s.grid_loc, p1)
            dis2 = math.dist(s.grid_loc, p2)

            if dis1 <= dis2:
                valid = self.add_wire(s, self.pts[p1])
                # if the first part of the corner wire is valid, recursiveley add the second half
                if valid:
                    self.add_wire(self.pts[p1], e)
            else:
                # if the first part of the corner wire is valid, recursiveley add the second half
                valid = self.add_wire(s, self.pts[p2])
                if valid:
                    self.add_wire(self.pts[p2], e)

    def add_component(self, gcoord, orientation, type_indicator):
        center_pt = self.pts[gcoord]
        x = gcoord[0]
        y = gcoord[1]

        center_pt.restricted_for_wires = True
        x, y = gcoord[0], gcoord[1]

        t1_pt = self.pts[
            (x-1, y)] if orientation == "horizontal" else self.pts[(x, y+1)]
        t2_pt = self.pts[
            (x+1, y)] if orientation == "horizontal" else self.pts[(x, y-1)]

        if type_indicator == "Resistor":
            new_component = Resistor(center_pt, t1_pt, t2_pt, orientation)
        elif type_indicator == "Source":
            new_component = VoltageSource(center_pt, t1_pt, t2_pt, orientation)

        new_component.restrict_points(self.pts)

        self.components[gcoord] = new_component
        self.check_new_component_connection(new_component)
        self.new_components.add(new_component)

        if self.is_complete_circuit():
            self.determine_connection_types()


    def create_wire_point(self, pt):
        if not pt.restricted_for_wires:
            # if wire_pts is empty, this will be the starting point of the wire
            if not self.wire_pts:
                self.wire_pts.append(pt)
                return -1
            # if wire_pts is not empty, this will be the ending point of the wire
            else:
                start = self.wire_pts.pop()
                end = pt
                # call add_wire_wrapper here
                self.add_wire_wrapper(start, end)
                # if new_wire_stack is not empty, then the wire is valid
                if self.new_wire_stack:
                    return self.new_wire_stack
                # if new_wire_stack is empty, the wire was not valid
                else:
                    # -2 indicates to stop mouse tracking for display wire (user tried to place wire across an existing component)
                    return -2
        else:
            return -2

    def is_valid_wire(self, s, e):
        orientation, direction = self.det_wire_orientation(
            s.grid_loc, e.grid_loc)

        s_x = s.grid_loc[0]
        s_y = s.grid_loc[1]
        e_x = e.grid_loc[0]
        e_y = e.grid_loc[1]
        line_pts = []
        if orientation == "vertical":
            if s_y < e_y:
                line_pts = [self.pts[(s_x, y)] for y in range(s_y, e_y)]
            else:
                line_pts = [self.pts[(s_x, y)] for y in range(e_y, s_y)]

        elif orientation == "horizontal":
            if s_x < e_x:
                line_pts = [self.pts[(x, s_y)] for x in range(s_x, e_x)]
            else:
                line_pts = [self.pts[(x, s_y)] for x in range(e_x, s_x)]

        for pt in line_pts:
            if pt.restricted_for_wires:
                return False

        # if none of the points from the start point to the end point are restricted, return True, it is a valid wire
        else:
            return True

    def remove_wire(self, w):  
        self.wires.remove(w)
        node = w.node
        node.remove_wire(w)
        for pt in w.points:
            pt.default()

    # might make this a wire method too
    def det_wire_orientation(self, s, e):
        s_x = s[0]
        s_y = s[1]
        e_x = e[0]
        e_y = e[1]
        orientation = ""
        direction = ""

        if s_x == e_x:
            orientation = "vertical"
            if s_y < e_y:
                direction = "down"      # increasing
            else:
                direction = "up"        # decreasing
        elif s_y == e_y:
            orientation = "horizontal"
            if s_x < e_x:
                direction = "right"     # increasing
            else:
                direction = "left"      # decreasing

        return orientation, direction

    def remove_component(self, pt):
        gcoord = pt.grid_loc
        component = self.components.pop(gcoord)
        self.new_components.discard(component)

        for x, y in component.restricted_points:
            self.pts[(x, y)].restricted = False

        for c in component.parallel_connections:
            c.parallel_connections.remove(component)
        
        for c in component.series_connections:
            c.series_connections.remove(component)

