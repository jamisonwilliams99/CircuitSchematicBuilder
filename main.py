from tkinter import *

class Grid():
    def __init__(self):
        self.root = root
        self.pts = {}
        


class Point():
    def __init__(self, scr_coord, grid_coord):
        self.loc = scr_coord
        self.grid_loc = grid_coord

  

def conv_screen_to_grid(x_pos, y_pos):
    x = x_pos / 10
    y = y_pos / 10
    return (round(x), round(y))


def grid_click(event):
    grid_coord = conv_screen_to_grid(event.x, event.y)
    #print(grid_coord)



root = Tk()

CANVAS_HEIGHT = 600
CANVAS_WIDTH = 600
NUM_PTS = CANVAS_HEIGHT // 10


canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

grid = Grid()


for y in range(1, NUM_PTS):
    for x in range(1, NUM_PTS):
        x1 = x*10
        y1 = y*10
        x2 = x*12
        y2 = y*12
        mid_pt = ((x1+x2)/2, (y1+y2)/2)
        canvas.create_oval(x*10, y*10, x*10+2, y*10+2)
        grid.pts[str((x,y))] = Point(mid_pt, (x,y))

canvas.bind("<Button-1>", grid_click)

root.mainloop()