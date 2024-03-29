import tkinter as tk
from tkinter import *

from tkinter import ttk
from ttkthemes import themed_tk as tk

from grid import *
from component import *

"""
Circuit Schematic Builder

Allows the user to build circuit schematics and input values to different components
in the schematic. 

"""


# Constants
CANVAS_HEIGHT = 600
CANVAS_WIDTH = 600
NUM_PTS = CANVAS_HEIGHT // 10


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

def conv_grid_to_screen(gcoord):
    x = gcoord[0]*10
    y = gcoord[1]*10
    return x, y


class CircuitSim:
    def __init__(self, master):
        self.master = master

        # colors
        self.bg_color = "black"
        self.item_color = "white"

        # runtime flags
        self.resistor_activated = False
        self.wire_activated = False
        self.source_activated = False
        self.select_activated = False
        self.mouse_tracker_activated = False
        self.component_is_selected = False
        self.user_clicked_wire = False

        self.component_orientation = "horizontal"
        self.selected_component = None
        self.start_pt = None
        self.component_window = None
        self.track_stack = []

        # stores all of the canvas circle objects that mark the grid points
        self.grid_dots = []

        self.master.title("Circuit Schematic Builder")

        self.menu_frame = Frame(self.master)
        self.menu_frame.pack()

        self.wire_img = PhotoImage(file="./images/wire.png")
        self.wire_button = ttk.Button(self.menu_frame, width=20, image=self.wire_img,
                                      takefocus=False, command=self.activate_wire)

        self.wire_button.grid(row=0, column=0, padx=3, pady=5)

        self.resistor_img = PhotoImage(file="./images/resistor.png")
        self.resistor_button = ttk.Button(
            self.menu_frame, width=20, image=self.resistor_img, takefocus=False, command=self.activate_resistor)
        self.resistor_button.grid(row=0, column=1, padx=3, pady=5)

        self.source_img = PhotoImage(file="./images/source.png")
        self.source_button = ttk.Button(
            self.menu_frame, width=20, image=self.source_img, takefocus=False, command=self.activate_source)
        self.source_button.grid(row=0, column=2, padx=3, pady=5)

        self.select_img = PhotoImage(file="./images/mouse.png")
        self.select_button = ttk.Button(
            self.menu_frame, width=20, image=self.select_img, takefocus=False, command=self.activate_select)
        self.select_button.grid(row=0, column=3, padx=3, pady=5)

        self.clear_button = ttk.Button(
            self.menu_frame, width=5, text="Clear", takefocus=False, command=self.clear)
        self.clear_button.grid(row=0, column=4, padx=3, pady=5)


        self.canvas = None
        self.initiate_canvas()

        self.grid = Grid()
        self.draw_grid()

    def initiate_canvas(self):
        self.canvas = Canvas(self.master, width=CANVAS_WIDTH,
                             height=CANVAS_HEIGHT, bg=self.bg_color)
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.bind("<Button-1>", self.grid_click)
        self.canvas.bind("<Motion>", self.track_mouse_pos)
        self.canvas.bind("<Key-r>", self.rotate_component)
        self.canvas.bind("<Key-e>", self.delete_component)

    def switch_color_mode(self):
        self.bg_color = "white" if self.bg_color == "black" else "black"
        self.item_color = "black" if self.item_color == "white" else "white"
        self.canvas.configure(bg=self.bg_color)

    # draws the grid and also connects the maps the visual points to the points in the grid backend
    def draw_grid(self):
        for y in range(1, NUM_PTS):
            for x in range(1, NUM_PTS):
                x1 = x*10
                y1 = y*10
                x2 = x*12
                y2 = y*12
                mid_pt = ((x1+x2)/2, (y1+y2)/2)
                self.grid_dots.append(self.canvas.create_oval(
                    x*10, y*10, x*10+2, y*10+2, fill=self.item_color))
                self.grid.pts[(x, y)] = Point((x1, y1), (x, y))

    def erase_grid(self):
        for dot in self.grid_dots:
            self.canvas.delete(dot)

    # determines what action to perfom when the user clicks on the grid
    def grid_click(self, event):
        if self.component_window is not None:
            self.close_component_window()

        grid_coord = conv_screen_to_grid(event.x, event.y)
        if self.wire_activated:
            self.record_point(grid_coord)
        elif self.resistor_activated:
            self.place_component(grid_coord)
        elif self.source_activated:
            self.place_component(grid_coord)
        elif self.select_activated:
            self.select_component(grid_coord)

    # records start/end point of a wire
    def record_point(self, gcoord):
        # return value of create_wire_point() could be a list of one or two wires

        #TODO: CHANGE DICTIONARY ACESS
        point = self.grid.pts[gcoord]
        # could also be -1 if either only one point has been selected
        new_wires = self.grid.create_wire_point(point)
        # or if two points have been selected but it does not form a valid wire
        if new_wires == -1:
            self.mouse_tracker_activated = True
            self.start_pt = point
        elif new_wires == -2:
            self.mouse_tracker_activated = False
            self.clear_temp_wires()
        else:
            self.place_wire(new_wires)
            self.mouse_tracker_activated = False

    def track_mouse_pos(self, event):
        if self.mouse_tracker_activated:
            self.clear_temp_wires()
            self.grid.track_stack.clear()
            
            
            e_g = conv_screen_to_grid(event.x, event.y)
            end_pt = self.grid.pts[e_g]

            self.track_stack = self.grid.add_temp_wire(self.start_pt, end_pt)

            for wire, valid in self.track_stack:
                color = self.item_color if valid else "red"
                wire.draw(self.canvas, color)

    def clear_temp_wires(self):
        for wire, valid in self.track_stack:
            wire.erase(self.canvas)
        self.track_stack.clear()

    # takes in a argument in the form of a stack of wire objects to be drawn to the screen
    # and calls each wire objects draw() method. The stack can contain one or two wire objects
    def place_wire(self, wires):
        # while there is another wire in the stack
        while wires:
            wire = wires.pop(0)
            wire.draw(self.canvas, self.item_color)
        self.clear_temp_wires()

        self.canvas.after(50)
        self.canvas.update()

    # removes all wires/components from the grid
    def clear(self):
        for wire in self.grid.wires:
            for line in wire.lines:
                self.canvas.delete(line)

        for component in self.grid.components.values():
            for line in component.lines:
                self.canvas.delete(line)

        self.clear_temp_wires()

        #self.selected_component.selected = False
        #self.selected_component = None

        self.grid.default_grid()
        self.canvas.after(50)
        self.canvas.update()

    # is called when the wire button is pressed, the user wants to place a wire
    def activate_wire(self):
        self.deactivate_all_components()
        self.wire_activated = True

    # is called when the resistor button is pressed, the user wants to place a resistor
    def activate_resistor(self):
        self.deactivate_all_components()
        self.resistor_activated = True
    
    def activate_source(self):
        self.deactivate_all_components()
        self.source_activated = True

    # is called when the select button is pressed, the user wants to select a component on the grid
    def activate_select(self):
        self.deactivate_all_components()
        self.select_activated = True

    # is called anytime the user clicks a button. Sets all button flags to false to ensure that none are activated at the same time
    def deactivate_all_components(self):
        self.wire_activated = False
        self.resistor_activated = False
        self.source_activated = False
        self.select_activated = False

    # takes in a grid coordinate as an argument, uses that coordinate to look up the point object in the grid.pts dictionary,
    # makes sure that the point is not restricted, and then creates a new resistor object, and then calls that new resistor objects draw() method
    def place_component(self, gcoord):
        point = self.grid.pts[gcoord]
        if not point.restricted_for_components:
            if self.resistor_activated:
                self.grid.add_component(gcoord, self.component_orientation, "Resistor")
            elif self.source_activated:
                self.grid.add_component(gcoord, "vertical", "Source")

            component = self.grid.components[gcoord]
            component.draw(self.canvas, self.item_color)
            self.canvas.after(50)
            self.canvas.update()

    # rotates the selected component when the user presses 'r'
    def rotate_component(self, event):
        if self.resistor_activated:
            if self.component_orientation == "horizontal":
                self.component_orientation = "vertical"
            elif self.component_orientation == "vertical":
                self.component_orientation = "horizontal"

        elif self.component_is_selected:
            self.selected_component.rotate(self.canvas)
            self.canvas.after(50)
            self.canvas.update()

    # selects the component (or wire) that the user clicks on
    def select_component(self, gcoord):
        try:
            # if there is not already a component selected
            if not self.component_is_selected:
                # user_clicked_wire -> boolean   # wire -> Wire or None(if function returns false)
                self.user_clicked_wire, wire = self.clicked_wire(gcoord)
                # if the selected component is a wire
                if self.user_clicked_wire:
                    self.selected_component = wire
                    self.selected_component.selected = True
                    self.component_is_selected = True
                    self.selected_component.draw(self.canvas, self.item_color)
                # the selected component is not a wire; it is some other component
                else:
                    self.selected_component = self.grid.components[gcoord]
                    self.selected_component.selected = True
                    self.component_is_selected = True
                    self.selected_component.draw(self.canvas, self.item_color)
                    self.display_component_window(gcoord)
            # there is already a component selected; in this case, deselect it and and reset all selection flags
            else:
                self.selected_component.selected = False
                self.component_is_selected = False
                self.user_clicked_wire = False
                self.selected_component.draw(self.canvas, self.item_color)
                self.selected_component = None
        except KeyError:
            pass

    def display_component_value(self, gcoord):
        x, y = conv_grid_to_screen(gcoord)
        val_str = str(self.selected_component.get_controlled_value()) + self.selected_component.symbol

        if self.selected_component.orientation == "vertical":
            x = x - 20 - len(val_str)*5
            y = y - 10
        elif self.selected_component.orientation == "horizontal":
            x = x - 20
            y = y - 30
    
        component_val_frame = ttk.Frame(self.master)
        component_val_label = ttk.Label(component_val_frame, text=val_str,background='black', foreground='white', font=('Arial', 7))
        component_val_label.pack()
        component_val_window = self.canvas.create_window(x, y, anchor='nw', window=component_val_frame)

    def display_component_window(self, gcoord):
        x, y = conv_grid_to_screen(gcoord)
        x, y = x+20, y+20

        def update_component():
            val = int(measurement_entry.get())
            self.selected_component.set_controlled_value(val)
            #self.display_component_value(gcoord)
        
        measurement = self.selected_component.measurement
        symbol = self.selected_component.symbol

        component_frame = ttk.Frame(self.master)

        name_label = ttk.Label(component_frame, text=self.selected_component.name)
        name_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0))

        measurement_entry = ttk.Entry(component_frame)
        current_val = str(self.selected_component.get_controlled_value())
        measurement_entry.insert(0, current_val)
        measurement_entry.grid(row=1, column=0, padx=(20, 3))

        measurement_label = ttk.Label(component_frame, text=symbol, width=2)
        measurement_label.grid(row=1, column=1)

        dependent_var_labels = []
        r = 2
        for key, value in self.selected_component.dependent_variables.items():
            text_str = "{}: {}{}".format(key, value[0], value[1])
            label = ttk.Label(component_frame, text=text_str)
            label.grid(row=r, column=0)
            r+=1

        update_button = ttk.Button(component_frame, text="Update", command=update_component)
        update_button.grid(row=r, column=0, padx=(20, 0))

        self.component_window = self.canvas.create_window(x, y, anchor='nw', window=component_frame)

    def close_component_window(self):
        self.canvas.delete(self.component_window)

    # erases the selected component from the grid when the user presses "e"
    def delete_component(self, event):
        if self.component_is_selected:
            # if the component that is selected is a wire
            if self.user_clicked_wire:
                # need to remove wire from screen and remove wire from grid
                self.grid.remove_wire(self.selected_component)
                self.selected_component.erase(self.canvas)
                self.component_is_selected = False
                self.wire_selected = False
                self.selected_component = None
            # the selected component is not a wire
            else:
                pt = self.selected_component.center_point
                self.selected_component.erase(self.canvas)
                self.grid.remove_component(pt)
                self.component_is_selected = False
                self.selected_component = None

    # determines if the user clicks on a wire to select it
    # returns true if the point that is clicked on is a point that a wire crosses through
    # If it returns true, it also returns the wire that the point is apart of
    def clicked_wire(self, gcoord):
        pt = self.grid.pts[gcoord]
        for wire in self.grid.wires:
            if pt in wire.points:
                return True, wire
        else:
            return False, None


def main():

    root = tk.ThemedTk()
    root.get_themes()
    root.set_theme("radiance")

    sim = CircuitSim(root)

    root.mainloop()


if __name__ == "__main__":
    main()
