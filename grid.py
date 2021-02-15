import math

# Helper functions
def conv_screen_to_grid(x_pos, y_pos):
    x = round(x_pos/10)
    y = round(y_pos/10)
    if x == 0:
        x = 1
    if y == 0:
        y = 1
    if x == 60:
        x = 59
    if y == 60:
        y = 59
    
    return (x, y)


class Resistor:
    def __init__(self, pt):
        self.center_point = pt
        self.orientation = "horizontal"
        self.lines = []
    
    def draw(self, canvas):
        center = self.center_point.loc
        if self.orientation == "horizontal":
            beginning = (center[0]-10, center[1]) 
            end = (center[0]+10, center[1])
            self.lines.append(canvas.create_line(beginning[0], beginning[1], beginning[0]+5, beginning[1]+5, fill="white"))
            self.lines.append(canvas.create_line(beginning[0]+5, beginning[1]+5, beginning[0]+10, beginning[1]-5, fill="white"))
            self.lines.append(canvas.create_line(beginning[0]+10, beginning[1]-5, beginning[0]+15, beginning[1]+5, fill="white"))
            self.lines.append(canvas.create_line(beginning[0]+15, beginning[1]+5, beginning[0]+20, beginning[1]-5, fill="white"))
            self.lines.append(canvas.create_line(beginning[0]+20, beginning[1]-5, end[0], end[1] ,fill="white"))
        elif self.orientation == "vertical":
            beginning = (center[0], center[1]-10) 
            end = (center[0], center[1]+10)

    def rotate(self):
        if self.orientation == "horizontal":
            self.orientation = "vertical"
        elif self.orientation == "vertical":
            self.orientation = "horizontal"

class Wire:
    def __init__(self, pts):
        self.points = pts       # list of Point objects that the wire passes through
        

class Point():
    def __init__(self, scr_coord, grid_coord):
        self.loc = scr_coord
        self.grid_loc = grid_coord
        self.restricted = False
        self.is_component_center = False
        

class Grid():
    def __init__(self):
        self.pts = {}
        self.selected_points = []   # contains the points in the grid that are the start/end points of a wire
        self.components = {}
        self.wires = []   

    def select_wire_point(self, gcoord):
        scr_coord = self.pts[str(gcoord)].loc       # screen coordinate of the point
        self.selected_points.append(scr_coord)      
        if len(self.selected_points) == 2:          
            
            start = self.selected_points[0]
            end = self.selected_points[1]

            x1 = start[0]
            y1 = start[1]
            x2 = end[0]
            y2 = end[1]

            # if this returns true, two lines will be required to reach end point
            if x1 != x2 and y1 != y2:
                p1 = (x1, y2)
                p2 = (x2, y1)

                dis1 = math.dist(start, p1)
                dis2 = math.dist(start, p2)

                # determine shortest path to endpoint using two lines
                if dis1 <= dis2:
                    if self.is_valid_wire(start, p1):
                        self.add_wire(start, p1)
                        self.selected_points[1] = p1
                    else:
                        self.selected_points.clear() 
                        return -1
                else:
                    if self.is_valid_wire(start, p2):
                        self.add_wire(start, p2)
                        self.selected_points[1] = p2
                    else:
                        self.selected_points.clear()
                        return -1

                if self.is_valid_wire(self.selected_points[1], end):
                    self.add_wire(self.selected_points[1], end)
                    self.selected_points.append(end)
                else:
                    self.selected_points.clear()
                    return -1
            
                temp_list = self.selected_points.copy()
                self.selected_points.clear()
                return temp_list

            else:
                if self.is_valid_wire(start, end):
                    self.add_wire(start, end)
                    temp_list = self.selected_points.copy()
                    self.selected_points.clear()
                    return temp_list
                else:
                    self.selected_points.clear()
                    return -1

        else:
            return -1
    


    def add_resistor(self, gcoord):
        center_pt = self.pts[str(gcoord)]
        x = gcoord[0]
        y = gcoord[1]
        restricted_points = [
            (x-1, y), (x-2, y), (x+1, y), (x+2, y),
            (x-2, y+1), (x-1, y+1), (x, y+1), (x+1, y+1), (x+2, y+1),
            (x-2, y-1), (x-1, y-1), (x, y-1), (x+1, y-1), (x+2, y-1)
        ]
        
        for x, y in restricted_points:
            self.pts[str((x,y))].restricted = True
        
        self.components[str(gcoord)] = Resistor(center_pt)

    # creates wire object and adds it to the logical grid
    def add_wire(self, s, e):
        s_g = conv_screen_to_grid(s[0], s[1])
        e_g = conv_screen_to_grid(e[0], e[1])
        
        orientation = self.det_wire_orientation(s, e)

        wire_pts = []
        if orientation == "vertical":
            for y in range(s_g[1], e_g[1]+1):
                pt = self.pts[str((s_g[0],y))]
                pt.restricted = True
                wire_pts.append(pt)
        
        if orientation == "horizontal":
            for x in range(s_g[0], e_g[0]+1):
                pt = self.pts[str((x,s_g[1]))]
                pt.restricted = True
                wire_pts.append(pt)
        
        self.wires.append(Wire(wire_pts))
        



        
    def is_valid_wire(self, s, e):
        orientation = self.det_wire_orientation(s, e)
        s_x = s[0]
        s_y = s[1]
        e_x = e[0]
        e_y = e[1]

        # wire is a vertical line
        if orientation == "vertical":
            for component in self.components.values():
                center = component.center_point.loc
                c_x = center[0]     # x value of component center point
                c_y = center[1]     # y value of component center point

                # if the center point of the component has same x as vertical line
                if c_x == s_x:

                    # if the line crosses through the center point of the component, return false -> not a valid wire 
                    if (c_y > s_y and c_y < e_y) or (c_y < s_y and c_y > e_y):
                        return False
        
        # wire is a horizontal line    
        elif orientation == "horizontal":                                           
            for component in self.components.values():                                       
                center = component.center_point.loc                                 
                c_x = center[0]     # x value of component center point                                                    
                c_y = center[1]     # y value of component center point

                # if the center point of the component has same y as vertical line
                if c_y == s_y:

                    # if the line crosses through the center point of the component, return false -> not a valid wire
                    if (c_x > s_x and c_x < e_x) or ( c_x > s_x and c_x < e_x):
                        return False
        
        return True

    def det_wire_orientation(self, s, e):
        s_x = s[0]
        s_y = s[1]
        e_x = e[0]
        e_y = e[1]
        orientation = ""

        if s_x == e_x:
            orientation = "vertical"        
        elif s_y == e_y:
            orientation = "horizontal"
        
        return orientation




