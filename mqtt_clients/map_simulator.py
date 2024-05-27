from tkinter import *
import Pmw
import config
import random
from PIL import Image,ImageTk
from map_pathfinder import Node, Occupant, a_star, scan, manhattan_distance
from rover import Rover, Mode

def draw_grid():

    # Initialize a grid of Label objects for empty cells
    for i in range(rows):
        for j in range(cols):
            label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
            label.grid(row=i, column=j)
    
    # Add static objects to the grid
    for row in grid:
        for cell in row:
            if cell.occupant == Occupant.OBSTACLE:
                label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
                label.grid(row=cell.r, column=cell.c)
                label.config(height=ch, width=cw, bg="brown")

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

    label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=r, column=c)
    label.config(image=flag_icon[team_id], height=ch, width=cw)
    grid[r][c].occupant = Occupant.FLAG
    
    # Add tooltip for flag
    flag_tt = Pmw.Balloon(root)
    flag_tt.bind(label, f"Team {team_id} - Flag")

# Update the rover position on the grid
def update_rover_position(rover, new_pos, is_start=False):

    # Clear the previous position if not the starting position
    if not is_start:
        label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
        label.grid(row=rover.r, column=rover.c)
        grid[rover.r][rover.c].occupant = Occupant.EMPTY

    # Set the new position
    rover.r = new_pos.r
    rover.c = new_pos.c
    rover.my_grid[rover.r][rover.c].visited = True
    grid[rover.r][rover.c].occupant = Occupant.ROVER

    # Update the grid with the new position
    label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=rover.r, column=rover.c)
    label.config(image=rover_image[rover.team_id], height=ch, width=cw)
    
    # Add tooltip for rover
    rover_tt = Pmw.Balloon(root)
    rover_tt.bind(label, f"Team {rover.team_id} - Rover {rover.group_id}")

# Move rover towards a specified cell using A* algorithm
def move_rover(rover):
    
    start = Node(rover.r, rover.c)

    # Assuming the rover knows the location of the flag
    if rover.mode == Mode.HEADING_TO_FLAG:
        goal = Node(rows-1, int(cols / 2)) 
        path = a_star(rows, cols, start, goal, obstacles)

    # Scan the environment for an unexplored area
    if rover.mode == Mode.EXPLORING:
        scan(rover, grid)
        my_grid = rover.my_grid

        # TODO: Need a better way to explore (frontier-based exploration?)
        # Set the goal to be the farthest unexplored cell
        max_distance = 0
        goal = None
        for row in my_grid:
            for cell in row:
                if not cell.visited and cell.occupant == Occupant.UNKNOWN:
                    distance = manhattan_distance(start, cell)
                    if distance > max_distance:
                        max_distance = distance
                        goal = cell

        # Explore frontier
        path = a_star(rows, cols, start, goal, rover.get_all_obstacles())
    
    # Update the rover position by moving one step along the path
    if path and len(path) > 1:
        r, c = path[1]    
        update_rover_position(rover, Node(r,c))
        # Rover has crashed!
        if grid[r][c].occupant == Occupant.OBSTACLE:
            log_text.insert(END, f"Team {rover.team_id} - Rover {rover.group_id} has crashed into an obstacle\n")

def start_simulation():

    # Move the rovers synchronously towards their destination
    rover[0][0].mode = Mode.EXPLORING
    move_rover(rover[0][0])
    #move_rover(rover[0][1])
    #move_rover(rover[1][0])
    #move_rover(rover[1][1])

    # Run the simulation again after 1 second
    simulate = root.after(1000, start_simulation)
    
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
    ch = 50                 # height of each cell in pixels
    cw = 50                  # width of each cell in pixels

    # Initialize icons
    blank = PhotoImage()
    red_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redrobot.png").resize((ch, cw)))
    blue_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/bluerobot.png").resize((ch,cw)))
    rover_image = [red_image, blue_image]
    red_flag_icon = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redflag.png").resize((ch, cw)))
    blue_flag_icon = ImageTk.PhotoImage(Image.open("mqtt_clients/images/blueflag.png").resize((ch, cw)))
    flag_icon = [red_flag_icon, blue_flag_icon]

    # Create the the gridboard
    grid = [[Node(r, c) for c in range(cols)] for r in range(rows)]
    for row in grid:
        for cell in row:
            cell.occupant = Occupant.EMPTY
    obstacles = generate_obstacles(config.NUM_OBSTACLES)
    draw_grid()
    
    # Initialize flag positions on grid (half way between the groups)
    red_flag = Node(0, int(cols / 2)) 
    blue_flag = Node(rows-1, int(cols / 2))
    set_flag_position(0, 0, int(cols / 2))
    set_flag_position(1, rows-1, int(cols / 2))

    # Add a textbox showing log of events on right of the grid
    log_text = Text(root, height=30, width=50, bg="black", fg="white", font=("Arial", 16))
    log_text.grid(row=0, column=cols+1, rowspan=rows, padx=50, pady=10, sticky=N+S+E+W)
    log_text.insert(END, "Event Log:\n")

    # Initialize team positions on grid
    rover = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    for i in range(config.NUM_TEAMS):
        for j in range(2):
            rover[i][j] = Rover(i, j, i*(rows-1), j*(cols-1), 0)
            start_pos = Node(i*(rows-1), j*(cols-1))
            update_rover_position(rover[i][j], start_pos, True)
            log_text.insert(END, f"Team {i} - Rover {j} Ready\n")

    # Start the main event loop
    root.mainloop()