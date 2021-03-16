import math


class Wire:
    def __init__(self, start, end, grid_pts, orientation, direction, is_temp_wire=False):
        self.grid_pts = grid_pts    # dictionary of points in the grid
        self.points = []           # list of Point objects that the wire passes through
        self.start_pt = start
        self.end_pt = end
        self.lines = []
        self.color = "white"
        self.selected = False
        self.node = None

        # wire could be connected to some point or another wire
        self.start_pt_connection = None
        self.end_pt_connection = None

        self.determine_wire_points(orientation, direction)

        if not is_temp_wire:
            self.connect_wire_to_pt()

    def __str__(self):
        return 'Wire'

    def __repr__(self):
        return 'Wire: {} -> {}'.format(self.start_pt.grid_loc, self.end_pt.grid_loc)

    def set_node(self, node):
        self.node = node

    def draw(self, canvas, c):
        self.color = "blue" if self.selected else c
        s_x = self.start_pt.loc[0]
        s_y = self.start_pt.loc[1]
        e_x = self.end_pt.loc[0]
        e_y = self.end_pt.loc[1]

        if s_x != e_x and s_y != e_y:
            p1 = (s_x, e_y)
            p2 = (e_x, s_y)
            dis1 = math.dist((s_x, s_y), p1)
            dis2 = math.dist((s_x, s_y), p2)

            if dis1 <= dis2:
                self.lines.append(canvas.create_line(
                    s_x, s_y, p1[0], p1[1], fill=self.color))
                self.lines.append(canvas.create_line(
                    p1[0], p1[1], e_x, e_y, fill=self.color))
            else:
                self.lines.append(canvas.create_line(
                    s_x, s_y, p2[0], p2[1], fill=self.color))
                self.lines.append(canvas.create_line(
                    p2[0], p2[1], e_x, e_y, fill=self.color))

        else:
            self.lines.append(canvas.create_line(
                s_x, s_y, e_x, e_y, fill=self.color))

    def erase(self, canvas):
        for line in self.lines:
            canvas.delete(line)

    def determine_wire_points(self, orientation, direction):
        s_g = self.start_pt.grid_loc
        e_g = self.end_pt.grid_loc

        s_x, s_y = s_g[0], s_g[1]
        e_x, e_y = e_g[0], e_g[1]

        if orientation == "vertical" and direction == "down":
            for y in range(s_y, e_y+1):
                pt = self.grid_pts[str((s_x, y))]
                self.points.append(pt)
        elif orientation == "vertical" and direction == "up":
            for y in range(e_y, s_y+1):
                pt = self.grid_pts[str((s_x, y))]
                self.points.append(pt)
        elif orientation == "horizontal" and direction == "right":
            for x in range(s_x, e_x+1):
                pt = self.grid_pts[str((x, s_y))]
                self.points.append(pt)
        elif orientation == "horizontal" and direction == "left":
            for x in range(e_x, s_x+1):
                pt = self.grid_pts[str((x, s_y))]
                self.points.append(pt)
    
    def connect_wire_to_pt(self):
        for pt in self.points:
            pt.set_wire(self)

    def make_connection(self, pt, ciruit_object):
        if pt is self.start_pt:
            self.start_pt_connection = ciruit_object
            ciruit_object.make_connection(pt, self)
        elif pt is self.end_pt:
            self.end_pt_connection = ciruit_object
            ciruit_object.make_connection(pt, self)
  


class Node:
    def __init__(self, wire_stack):
        self.wires = []
        self.add_wire(wire_stack)

    def add_wire(self, wire_stack):
        for wire in wire_stack:
            self.wires.append(wire)
            wire.set_node(self)

    def __repr__(self):
        s = [repr(wire) for wire in self.wires]
        return str(s)



class Component:
    def __init__(self, pt, t1_pt, t2_pt, restricted_pts, orientation):
        self.center_point = pt
        self.orientation = orientation
        self.lines = []
        self.restricted_points = restricted_pts
        self.selected = False
        self.color = "white"
        self.type = "Undefined"
        self.series_connections = set()
        self.parallel_connections = set()

        # terminal will be on the left/bottom depending on orientation
        self.t1 = self.Terminal(t1_pt)
        # terminal will be on the right/top depending on orientation
        self.t2 = self.Terminal(t2_pt)

    def __str__(self):
        print(self.type)

    def __repr__(self):
        return '{} at {}'.format(self.type, self.center_point.grid_loc)

    def make_connection(self, wire, pt):
        if pt.grid_loc == self.t1.pt.grid_loc:
            self.t1.wire = wire
            print('connected to wire at t1')
        elif pt.grid_loc == self.t2.pt.grid_loc:
            self.t2.wire = wire
            print('connected to wire at t2')

    def erase(self, canvas):
        for line in self.lines:
            canvas.delete(line)

    # each component will have two terminal objects which are then connected to Node objects
    # it may be best to not make the terminal class an inner class so that it can refer to the component 
    class Terminal:
        def __init__(self, pt):
            self.pt = pt
            self.wire = None

        def __repr__(self):
            return 'Terminal connected to {}'.format(repr(self.wire))




class Resistor(Component):
    def __init__(self, pt, t1_pt, t2_pt, restricted_pts, orientation):
        super().__init__(pt, t1_pt, t2_pt, restricted_pts, orientation)
        self.type = "Resistor"

    def draw(self, canvas, c):
        self.color = "blue" if self.selected else c
        center = self.center_point.loc

        # if the resistor has already been drawn (it is being redrawn due to being selected or rotated)
        if self.lines:
            self.erase(canvas)

        if self.orientation == "horizontal":
            beginning = (center[0]-10, center[1])
            end = (center[0]+10, center[1])
            self.lines.append(canvas.create_line(
                beginning[0], beginning[1], beginning[0]+3, beginning[1]-5, fill=self.color))
            self.lines.append(canvas.create_line(
                beginning[0]+3, beginning[1]-5, beginning[0]+6, beginning[1]+5, fill=self.color))
            self.lines.append(canvas.create_line(
                beginning[0]+6, beginning[1]+5, center[0], center[1]-5, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0], center[1]-5, center[0]+3, center[1]+5, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]+3, center[1]+5, center[0]+6, center[1]-5, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]+6, center[1]-5, center[0]+8, center[1]+5, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]+8, center[1]+5, end[0], end[1], fill=self.color))
        elif self.orientation == "vertical":
            beginning = (center[0], center[1]+10)
            end = (center[0], center[1]-10)
            self.lines.append(canvas.create_line(
                beginning[0], beginning[1], beginning[0]-5, beginning[1]-3, fill=self.color))
            self.lines.append(canvas.create_line(
                beginning[0]-5, beginning[1]-3, beginning[0]+5, beginning[1]-6, fill=self.color))
            self.lines.append(canvas.create_line(
                beginning[0]+5, beginning[1]-6, center[0]-5, center[1], fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]-5, center[1], center[0]+5, center[1]-3, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]+5, center[1]-3, center[0]-5, center[1]-6, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]-5, center[1]-6, center[0]+5, center[1]-8, fill=self.color))
            self.lines.append(canvas.create_line(
                center[0]+5, center[1]-8, end[0], end[1], fill=self.color))

    def rotate(self, canvas):
        if self.orientation == "horizontal":
            self.orientation = "vertical"
            self.draw(canvas, self.color)
        elif self.orientation == "vertical":
            self.orientation = "horizontal"
            self.draw(canvas, self.color)





class VoltageSource(Component):
    def __init__(self, pt, t1_pt, t2_pt, restricted_pts, orientation):
        super().__init__(pt, t1_pt, t2_pt, restricted_pts, orientation)
        self.type = "Source"

    def draw(self, canvas, c):
        self.color = "blue" if self.selected else c
        center = self.center_point.loc

        if self.lines:
            self.erase(canvas)

        def draw_plus():
            plus_center = (center[0], center[1]-5)
            self.lines.append(canvas.create_line(
                plus_center[0]-2, plus_center[1], plus_center[0]+3, plus_center[1], fill=self.color))
            self.lines.append(canvas.create_line(
                plus_center[0], plus_center[1]-2, plus_center[0], plus_center[1]+3, fill=self.color))            

        def draw_minus():
            minus_center = (center[0], center[1]+5)
            self.lines.append(canvas.create_line(
                minus_center[0]-2, minus_center[1], minus_center[0]+3, minus_center[1], fill=self.color ))

        x1 = center[0]-10
        y1 = center[1]-10
        x2 = center[0]+10
        y2 = center[1]+10

        self.lines.append(canvas.create_oval(
            x1, y1, x2, y2, outline=self.color, fill='black'))
        draw_plus()
        draw_minus()


