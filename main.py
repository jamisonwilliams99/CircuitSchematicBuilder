import tkinter as tk
from tkinter import *
from grid import *

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
        # runtime flags
        self.resistor_activated = False
        self.wire_activated = False

        self.menu_frame = Frame(master)
        self.menu_frame.pack()

        self.wire_img = PhotoImage(file="./images/wire.png")
        self.wire_button = Button(self.menu_frame, width=20, image=self.wire_img, command=self.activate_wire)
        self.wire_button.grid(row=0, column=0, padx=3)

        self.resistor_img = PhotoImage(file="./images/resistor.png")
        self.resistor_button = Button(self.menu_frame, width = 20,image=self.resistor_img, command=self.activate_resistor)
        self.resistor_button.grid(row=0, column=1, padx=3)

        self.clear_button = Button(self.menu_frame, width=5, text="Clear", command=self.clear)
        self.clear_button.grid(row=0, column=2, padx=3)

        

        self.canvas = Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black")
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.bind("<Button-1>", self.grid_click)

        self.wires = []
        self.grid = Grid()
        self.draw_grid()
    
    # draws the grid and also connects the maps the visual points to the points in the grid backend
    def draw_grid(self):
        for y in range(1, NUM_PTS):
            for x in range(1, NUM_PTS):
                x1 = x*10
                y1 = y*10
                x2 = x*12
                y2 = y*12
                mid_pt = ((x1+x2)/2, (y1+y2)/2)
                self.canvas.create_oval(x*10, y*10, x*10+2, y*10+2, fill="white")
                self.grid.pts[str((x,y))] = Point((x1,y1), (x,y))
    
    # determines what action to perfom when the user clicks on the grid
    def grid_click(self, event):
        grid_coord = conv_screen_to_grid(event.x, event.y)

        if self.wire_activated:
            self.add_wire_point(grid_coord)
        elif self.resistor_activated:
            self.place_resistor(grid_coord)

    # records the start/end point of a wire    
    def add_wire_point(self, gcoord):
        point = self.grid.pts[str(gcoord)]

        pts = self.grid.select_wire_point(gcoord)
        if pts != -1:
            self.wires.append(self.canvas.create_line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], fill="white"))
            
            if len(pts) > 2:

                self.wires.append(self.canvas.create_line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], fill="white"))

            self.canvas.after(50)
            self.canvas.update()

    # removes all wires/components from the grid
    def clear(self):
        for wire in self.wires:
            self.canvas.delete(wire)
        for component in self.grid.components.values():
            for line in component.lines:
                self.canvas.delete(line)
        self.grid.selected_points.clear()
        self.canvas.after(50)
        self.canvas.update()

    def activate_wire(self):
        self.deactivate_all_components()
        self.wire_activated = True

    def activate_resistor(self):
        self.deactivate_all_components()
        self.resistor_activated = True

    def deactivate_all_components(self):
        self.wire_activated = False
        self.resistor_activated = False

    def place_resistor(self, gcoord):
        point = self.grid.pts[str(gcoord)]
        if not point.restricted:
            self.grid.add_resistor(gcoord)
            resistor = self.grid.components[str(gcoord)]
            resistor.draw(self.canvas)
            self.canvas.after(50)
            self.canvas.update()
        




def main():
    
    root = Tk()

    sim = CircuitSim(root)

    root.mainloop()




if __name__ == "__main__":
    main()


