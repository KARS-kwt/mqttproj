from email.policy import default
from tkinter import *
from turtle import update
import os
import Pmw
import config
import random
from PIL import Image,ImageTk
from map_pathfinder import Node, Occupant, a_star, manhattan_distance
from rover import Rover, Mode

def init_grid():
    grid = [[Node(r, c) for c in range(cols)] for r in range(rows)]
    for row in grid:
        for cell in row:
            root.rowconfigure(cell.r, weight=1)
            root.columnconfigure(cell.c, weight=1)
            label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
            label.grid(row=cell.r, column=cell.c, sticky=N+S+E+W)
            cell.occupant = Occupant.EMPTY
    
    root.rowconfigure(rows, weight=1)
    root.columnconfigure(cols, weight=1)        
    
    return grid

def draw_grid():
    
    # Populate the map with the groundtruth occupants using grid
    for row in grid:
        for cell in row:
            label = root.grid_slaves(cell.r, cell.c)[0]
            if cell.occupant == Occupant.EMPTY:
                label.config(bg=default_color, image=blank)
            if cell.occupant == Occupant.OBSTACLE:
                label.config(bg="brown", image=blank)  
            if cell.occupant == Occupant.REDFLAG:
                label.config(bg=default_color, image=red_flag_icon)
            if cell.occupant == Occupant.BLUEFLAG:
                label.config(bg=default_color, image=blue_flag_icon)
            if cell.occupant == Occupant.ROVER:
                label.config(bg=default_color, image=rover_image[cell.occupant_ref.team_id])

def create_start_button():
            
    # Create a button to start the simulation
    start_button = Button(root, text="Start Simulation", bg="green", fg="white", font=("Arial", 20), command=start_simulation)
    start_button.grid(row=rows, column=0, columnspan=cols)

    # Add tooltip for start button
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to start the simulation')

def generate_obstacles(num_rand_obstacles=10):

    # Obstacles are represented as a set of (r, c) tuples
    leftedge = int(cols / 2)-3 
    rightedge = int(cols / 2)+3
    obstacles = set()

    # Red base
    obstacles.update({(2, i) for i in range(leftedge)})
    obstacles.update({(2, i) for i in range(rightedge, cols)})

    # Blue base
    obstacles.update({(rows-3, i) for i in range(leftedge)})
    obstacles.update({(rows-3, i) for i in range(rightedge, cols)})

    # Generate random obstacles between the bases
    for _ in range(num_rand_obstacles):
        r = random.randint(3, rows-3)
        c = random.randint(0, cols-1)
        if (r, c) not in obstacles:
            obstacles.add((r, c))
    
    # Add obstacles to the grid
    for obstacle in obstacles:
        grid[obstacle[0]][obstacle[1]].occupant = Occupant.OBSTACLE
    
    return obstacles

# Set the flag position on the grid
def set_flag_position(team_id, r, c):

    grid[r][c].occupant = Occupant.REDFLAG if team_id == 0 else Occupant.BLUEFLAG
    label = root.grid_slaves(r, c)[0]
    label.config(image=flag_icon[team_id])
    
    # Add tooltip for flag
    flag_tt = Pmw.Balloon(root)
    flag_tt.bind(label, f"Team {team_id} - Flag")

# Update the log with a new message with timestamp
def update_log(message, add_timestamp=True):
    if add_timestamp:
        t = f"[{timestamp:04d}]:  "
    else:  
        t = ""
    log_text.insert(END, f"{t}{message}\n")
    log_text.see(END)

# Update the rover position on the grid
def update_rover_position(rover, new_pos, is_start=False):

    # Clear the previous position if not the starting position
    if not is_start:
        label = root.grid_slaves(rover.r, rover.c)[0]
        label.config(image=blank)
        grid[rover.r][rover.c].occupant = Occupant.EMPTY
        label.unbind("<Enter>")
        label.unbind("<Leave>")

    # Set the new position
    rover.r = new_pos.r
    rover.c = new_pos.c
    rover.my_grid[rover.r][rover.c].visited = True
    grid[rover.r][rover.c].occupant = Occupant.ROVER
    grid[rover.r][rover.c].occupant_ref = rover

    # Update the rover's label
    label = root.grid_slaves(rover.r, rover.c)[0]
    label.config(image=rover_image[rover.team_id])
    
    # Bind mouse click to toggle rover grid view
    label.bind("<Button-1>", toggle_rover_view)
    
    # Add tooltip for rover
    rover_tt = Pmw.Balloon(root)
    rover_tt.bind(label, f"Team {rover.team_id} - Rover {rover.group_id}")

def toggle_rover_view(event):
    
    global grid_view
    if not grid_view:
        r = event.widget.grid_info()["row"]
        c = event.widget.grid_info()["column"]
        rover = grid[r][c].occupant_ref

        rover_view = rover.my_grid
        for row in rover_view:
            for cell in row:
                color = default_color
                if cell.occupant == Occupant.EMPTY:
                    color = "white"
                elif cell.occupant == Occupant.OBSTACLE:
                    color = "brown"
                elif cell.occupant == Occupant.REDFLAG:
                    color = "red"
                elif cell.occupant == Occupant.BLUEFLAG:
                    color = "blue"
                elif cell.occupant == Occupant.ROVER:
                    color = "yellow"
                
                if cell.visited:
                    color = "lightgreen"
                    
                label = root.grid_slaves(cell.r, cell.c)[0]
                label.config(bg=color)
                
        grid_view = True
    else:
        draw_grid()
        grid_view = False

# Move rover towards a specified cell using A* algorithm
#TODO: move rover-related pathfinding to be in the rover module
def move_rover(rover):
    
    start = Node(rover.r, rover.c)
    path = None

    # Scan the environment for an unexplored area
    if rover.mode == Mode.EXPLORING:
        
        rover.scan(grid)
        my_grid = rover.my_grid

        # Check if found opponent's flag
        # TODO: There has to be a better way to do this
        found_flag = False
        for row in my_grid:
            for cell in row:
                if cell.occupant == Occupant.BLUEFLAG and rover.team_id == 0:
                    found_flag = True
                if cell.occupant == Occupant.REDFLAG and rover.team_id == 1:
                    found_flag = True
        if found_flag:
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has found the opponent's flag\n")
            rover.mode = Mode.HEADING_TO_FLAG
            return

        # Go to the farthest unvisited cell
        path = rover.explore()
    
    if rover.mode == Mode.HEADING_TO_FLAG:
        goal = Node((1-rover.team_id) * (rows-1), int(cols / 2)) 
        path = a_star(rows, cols, start, goal, obstacles)
    
    # Update the rover position by moving one step along the path
    if path and len(path) > 1:
        r, c = path[1]    
        if grid[r][c].occupant == Occupant.REDFLAG and rover.team_id == 1:
            # Rover has captured the flag!
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has captured the flag\n")
            rover.mode = Mode.RETURNING_TO_BASE
        if grid[r][c].occupant == Occupant.BLUEFLAG and rover.team_id == 0:
            # Rover has captured the flag!
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has captured the flag\n")
            rover.mode = Mode.RETURNING_TO_BASE
        if grid[r][c].occupant != Occupant.EMPTY:
            # Rover has crashed!
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has crashed into an obstacle\n")
        else:
            update_rover_position(rover, Node(r,c))
            rover.scan(grid)

def start_simulation():

    global timestamp
    timestamp += 1

    # Move the rovers synchronously towards their destination
    move_rover(rover[0][0])
    move_rover(rover[0][1])
    move_rover(rover[1][0])
    move_rover(rover[1][1])

    # Run the simulation again after 1 timestep
    simulate = root.after(config.TIMESTEP, start_simulation)
    
    # Function to stop the simulation (callback of the start/stop button)
    def stop_simulation():
        root.after_cancel(simulate)
        start_button.config(text="Start Simulation", bg="green", command=start_simulation)
        start_button_tt = Pmw.Balloon(root) 
        start_button_tt.bind(start_button,'Click here to start the simulation')

    # Get the start button from root
    start_button = root.grid_slaves(rows, 0)[0]
    start_button.config(text="Stop Simulation", bg="red", command=stop_simulation)
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to stop the simulation')

# For testing purposes
if __name__ == "__main__":

    # Create the main window
    root = Tk()
    Pmw.initialise(root)
    root.title("KARS Summer Camp 2024 - Map Simulator")

    # Initialize grid parameters
    rows = config.GRID_ROWS
    cols = config.GRID_COLS
    ch = 50                     # height of each cell in pixels
    cw = 50                     # width of each cell in pixels
    timestamp = 0
    default_color = root.cget("bg")
    grid_view = False

    # Initialize icons
    blank = PhotoImage()
    __imagelocation__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    red_image = ImageTk.PhotoImage(Image.open(os.path.join(__imagelocation__,"images/redrobot.png")).resize((ch, cw)))
    blue_image = ImageTk.PhotoImage(Image.open(os.path.join(__imagelocation__,"images/bluerobot.png")).resize((ch,cw)))
    rover_image = [red_image, blue_image]
    red_flag_icon = ImageTk.PhotoImage(Image.open(os.path.join(__imagelocation__,"images/redflag.png")).resize((ch, cw)))
    blue_flag_icon = ImageTk.PhotoImage(Image.open(os.path.join(__imagelocation__,"images/blueflag.png")).resize((ch, cw)))
    flag_icon = [red_flag_icon, blue_flag_icon]

    # Initialize the the gridboard
    grid = init_grid()
    obstacles = generate_obstacles(config.NUM_OBSTACLES)
    draw_grid()
    create_start_button()
    
    # Initialize flag positions on grid (half way between the groups)
    red_flag = Node(0, int(cols / 2)) 
    blue_flag = Node(rows-1, int(cols / 2))
    set_flag_position(0, 0, int(cols / 2))
    set_flag_position(1, rows-1, int(cols / 2))

    # Add a textbox showing log of events on right of the grid
    log_text = Text(root, height=30, width=50, bg="black", fg="white", font=("Arial", 16))
    log_text.grid(row=0, column=cols, rowspan=rows+1, padx=50, pady=10, sticky=N+S+E+W)
    update_log("Welcome to the KARS Summer Camp 2024!\nEvent Log:\n", False)

    # Initialize team positions on grid
    rover = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    for i in range(config.NUM_TEAMS):
        for j in range(2):
            rover[i][j] = Rover(i, j, i*(rows-1), j*(cols-1), 0)
            rover[i][j].scan(grid)
            start_pos = Node(i*(rows-1), j*(cols-1))
            update_rover_position(rover[i][j], start_pos, True)
            update_log(f"Team {i} - Rover {j} Deployed\n")

    # Start the main event loop
    root.mainloop()