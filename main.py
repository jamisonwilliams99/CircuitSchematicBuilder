import tkinter as tk
from tkinter import *

from tkinter import ttk
from ttkthemes import themed_tk as tk

from grid import *
from component import Wire

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
        self.track_stack = []

        # stores all of the canvas circle objects that mark the grid points
        self.grid_dots = []

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

        self.color_mode_button = ttk.Button(
            self.menu_frame, width=5, text="Light", takefocus=False, command=self.switch_color_mode)
        self.color_mode_button.grid(row=0, column=5, padx=3, pady=5)

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
                self.grid.pts[str((x, y))] = Point((x1, y1), (x, y))

    def erase_grid(self):
        for dot in self.grid_dots:
            self.canvas.delete(dot)

    # determines what action to perfom when the user clicks on the grid

    def grid_click(self, event):
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
        point = self.grid.pts[str(gcoord)]
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
            end_pt = self.grid.pts[str(e_g)]

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
    # TODO:make this a more general place_component(method)
    def place_resistor(self, gcoord):
        self.grid.add_resistor(gcoord, self.component_orientation)
        resistor = self.grid.components[str(gcoord)]
        resistor.draw(self.canvas, self.item_color)
        self.canvas.after(50)
        self.canvas.update()

    def place_source(self, gcoord):
        self.grid.add_source(gcoord, self.component_orientation)
        source = self.grid.components[str(gcoord)]
        source.draw(self.canvas, self.item_color)
        self.canvas.after(50)
        self.canvas.update()

    def place_component(self, gcoord):
        point = self.grid.pts[str(gcoord)]
        if not point.restricted:
            if self.resistor_activated:
                self.place_resistor(gcoord)
            elif self.source_activated:
                self.place_source(gcoord)


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
                    self.selected_component = self.grid.components[str(gcoord)]
                    self.selected_component.selected = True
                    self.component_is_selected = True
                    self.selected_component.draw(self.canvas, self.item_color)
            # there is already a component selected; in this case, deselect it and and reset all selection flags
            else:
                self.selected_component.selected = False
                self.component_is_selected = False
                self.user_clicked_wire = False
                self.selected_component.draw(self.canvas, self.item_color)
                self.selected_component = None
        except KeyError:
            pass

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
        pt = self.grid.pts[str(gcoord)]
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
