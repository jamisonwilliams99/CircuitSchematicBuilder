from component import *


class Point():
    def __init__(self, scr_coord, grid_coord):
        self.loc = scr_coord
        self.grid_loc = grid_coord
        self.restricted = False
        self.is_center_point = False
        # if the point is part of a wire, it will be set equal to that wire
        self.wire = None
        self.node = None

    def __repr__(self):
        return 'Point object at grid coordinate {}'.format(self.grid_loc)

    def set_wire(self, wire):
        if self.wire is None:
            self.wire = wire
            self.restricted = True

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
        self.wires = []
        self.new_wire_stack = []
        self.track_stack = [] # contains a list of tuples; (wire, is_wire_valid)
        self.wire_pts = []
        self.nodes = set() # set

    def default_grid(self):
        for pt in self.pts.values():
            pt.default()

        self.wires.clear()
        self.components.clear()
        self.nodes.clear()
        self.wire_pts.clear()

    def add_source(self, gcoord, orientation):
        center_pt = self.pts[str(gcoord)]
        x = gcoord[0]
        y = gcoord[1]
        restricted_points = [
            (x-1, y), (x-2, y), (x, y), (x+1, y), (x+2, y),
            (x-2, y+1), (x-1, y+1), (x, y+1), (x+1, y+1), (x+2, y+1),
            (x-2, y-1), (x-1, y-1), (x, y-1), (x+1, y-1), (x+2, y-1)
        ]

        for x, y in restricted_points:
            self.pts[str((x, y))].restricted = True

        center_pt.is_center_point = True
        x, y = gcoord[0], gcoord[1]

        t1_pt = self.pts[str(
            (x-1, y))] if orientation == "horizontal" else self.pts[str((x, y-1))]
        t2_pt = self.pts[str(
            (x+1, y))] if orientation == "horizontal" else self.pts[str((x, y+1))]

        self.components[str(gcoord)] = VoltageSource(
            center_pt, t1_pt, t2_pt, restricted_points, orientation)
        
        self.check_for_connection()


    def add_resistor(self, gcoord, orientation):
        center_pt = self.pts[str(gcoord)]
        x = gcoord[0]
        y = gcoord[1]

        # TODO: make restricting points a resistor function

        restricted_points = [
            (x-1, y), (x-2, y), (x, y), (x+1, y), (x+2, y),
            (x-2, y+1), (x-1, y+1), (x, y+1), (x+1, y+1), (x+2, y+1),
            (x-2, y-1), (x-1, y-1), (x, y-1), (x+1, y-1), (x+2, y-1)
        ]

        for x, y in restricted_points:
            self.pts[str((x, y))].restricted = True

        center_pt.is_center_point = True
        x, y = gcoord[0], gcoord[1]

        t1_pt = self.pts[str(
            (x-1, y))] if orientation == "horizontal" else self.pts[str((x, y-1))]
        t2_pt = self.pts[str(
            (x+1, y))] if orientation == "horizontal" else self.pts[str((x, y+1))]

        self.components[str(gcoord)] = Resistor(
            center_pt, t1_pt, t2_pt, restricted_points, orientation)

        self.check_for_connection()

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
                self.add_temp_wire(s, self.pts[str(p1)])
                self.add_temp_wire(self.pts[str(p1)], e)
            else:
                self.add_temp_wire(s, self.pts[str(p2)])
                self.add_temp_wire(self.pts[str(p2)], e)

        return self.track_stack

    # TODO: don't really like how this is done
    def check_for_connection(self):
        for component in self.components.values():
            for wire in self.wires:
                component.connect_wire(wire, wire.start_pt)
                component.connect_wire(wire, wire.end_pt)

    def make_wire_connection(self):
        pass

    def determine_component_connections():
        pass

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

    def print_all_nodes(self):
        print("NEW")
        for node in self.nodes:
            print(str(node))

    # calls add_wire() and then calls update_nodes()
    def add_wire_wrapper(self, s, e):
        self.add_wire(s, e)
        self.update_nodes()
        self.print_all_nodes()

    # creates wire object and adds it to the logical grid
    # returns a false flag if the wire is invalid
    def add_wire(self, s, e):
        s_g = s.grid_loc
        e_g = e.grid_loc

        orientation, direction = self.det_wire_orientation(s_g, e_g)

        # if orientation and direction are not empty strings (s and e make a straight line)
        # TODO: it may be better to have the is_valid_wire() method raise an exception and handle the
        # exception rather than just use a if else
        if orientation and direction:
            if self.is_valid_wire(s, e):
                new_wire = Wire(s, e, self.pts, orientation, direction)
                self.check_for_connection()
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
                valid = self.add_wire(s, self.pts[str(p1)])
                # if the first part of the corner wire is valid, recursiveley add the second half
                if valid:
                    self.add_wire(self.pts[str(p1)], e)
            else:
                # if the first part of the corner wire is valid, recursiveley add the second half
                valid = self.add_wire(s, self.pts[str(p2)])
                if valid:
                    self.add_wire(self.pts[str(p2)], e)

    # TODO: implement a way where this each new wire is added to a stack, where the wires are popped from the stack in main and drawn

    def create_wire_point(self, pt):
        if not pt.is_center_point:
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
                line_pts = [self.pts[str((s_x, y))] for y in range(s_y, e_y)]
            else:
                line_pts = [self.pts[str((s_x, y))] for y in range(e_y, s_y)]

        elif orientation == "horizontal":
            if s_x < e_x:
                line_pts = [self.pts[str((x, s_y))] for x in range(s_x, e_x)]
            else:
                line_pts = [self.pts[str((x, s_y))] for x in range(e_x, s_x)]

        for pt in line_pts:
            if pt.is_center_point:
                return False

        # if none of the points from the start point to the end point are restricted, return True, it is a valid wire
        else:
            return True

    def remove_wire(self, w):  # TODO
        for i, wire in enumerate(self.wires):
            if wire == w:
                self.wires.pop(i)
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
        component = self.components.pop(str(gcoord))

        for x, y in component.restricted_points:
            self.pts[str((x, y))].restricted = False
