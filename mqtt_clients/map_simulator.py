from calendar import c
from tkinter import *
import Pmw
import config
import random
from PIL import Image,ImageTk
from map_pathfinder import Node, a_star
from rover import Rover

def draw_grid(rows, columns):

    # Create a grid of Label objects
    for i in range(rows):
        for j in range(columns):
            label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
            label.grid(row=i, column=j)

    # Create a button to start the simulation
    start_button = Button(root, text="Start Simulation", bg="green", fg="white", font=("Arial", 20), command=start_simulation)
    start_button.grid(row=rows, column=0, columnspan=columns)

    # Add tooltip for start button
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to start the simulation')

def generate_obstacles(num_rand_obstacles=10):

    # Obstacles are represented as a set of (r, c) tuples

    leftedge = int(cols / 2)-3 
    rightedge = int(cols / 2)+3
    obstacles = set()

    # Create red base
    obstacles.update({(2, i) for i in range(leftedge)})
    obstacles.update({(2, i) for i in range(rightedge, cols)})

    # Create blue base
    obstacles.update({(rows-3, i) for i in range(leftedge)})
    obstacles.update({(rows-3, i) for i in range(rightedge, cols)})

    # Generate random obstacles between the bases
    for _ in range(num_rand_obstacles):
        r = random.randint(3, rows-3)
        c = random.randint(0, cols-1)
        if (r, c) not in obstacles:
            obstacles.add((r, c))
       
    for obstacle in obstacles:
        label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
        label.grid(row=obstacle[0], column=obstacle[1])
        label.config(height=ch, width=cw, bg="brown")
    
    return obstacles

def set_flag_position(team_id, r, c):

    label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=r, column=c)
    if team_id == 0:
        label.config(image=red_flag_icon, height=ch, width=cw)
    else:
        label.config(image=blue_flag_icon, height=ch, width=cw)
    
    # Add tooltip for flag
    flag_tt = Pmw.Balloon(root)
    flag_tt.bind(label, f"Team {team_id} - Flag")

def update_rover_position(rover, new_pos, is_start=False):

    if rover is None:
        return

    # Clear the previous position if not the start position
    if not is_start:
        label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
        label.grid(row=rover.r, column=rover.c)

    # Set the new position
    rover.r = new_pos.r
    rover.c = new_pos.c
    label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=rover.r, column=rover.c)
    if rover.team_id == 0:
        label.config(image=red_image, height=ch, width=cw)
    else:
        label.config(image=blue_image, height=ch, width=cw)
    
    # Add tooltip for rover
    rover_tt = Pmw.Balloon(root)
    rover_tt.bind(label, f"Team {rover.team_id} - Rover {rover.group_id}")

# Function to move the rover to the flag using A* algorithm
def move_rover(rover):
    
    if rover.team_id == 0:
        goal = Node(rows-1, int(config.GRID_COLS / 2)) 
    else:
        goal = Node(0, int(config.GRID_COLS / 2))
    start = Node(rover.r, rover.c)

    path = a_star(rows, cols, start, goal, obstacles)
    
    # Update the rover position by moving one step along the path
    if path and len(path) > 1:
        r, c = path[1]    
        update_rover_position(rover, Node(r,c))

def start_simulation():

    # Move the rovers synchronously
    move_rover(rover[0][0])
    #move_rover(rover[0][1])
    move_rover(rover[1][0])
    #move_rover(rover[1][1])

    # Add a log entry
    log_text.insert(END, "Rovers moved\n")

    # Run the simulation again after 1 second
    simulate = root.after(1000, start_simulation)
    
    # Function to stop the simulation (callback of the start/stop button)
    def stop_simulation():
        root.after_cancel(simulate)
        start_button.config(text="Start Simulation", bg="green", command=start_simulation)
        start_button_tt = Pmw.Balloon(root) 
        start_button_tt.bind(start_button,'Click here to start the simulation')

    # Get the start button from root
    start_button = root.grid_slaves(config.GRID_ROWS, 0)[0]
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

    # Initialize rover parameters
    blank = PhotoImage()
    red_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redrobot.png").resize((ch, cw)))
    blue_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/bluerobot.png").resize((ch,cw)))
    red_flag_icon = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redflag.png").resize((ch, cw)))
    blue_flag_icon = ImageTk.PhotoImage(Image.open("mqtt_clients/images/blueflag.png").resize((ch, cw)))
    red_flag = Node(0, int(cols / 2)) 
    blue_flag = Node(rows-1, int(cols / 2))

    # Draw the grid
    draw_grid(rows, cols)
    obstacles = generate_obstacles(90)

    # Initialize team positions on grid
    rover = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    for i in range(config.NUM_TEAMS):
        for j in range(2):
            rover[i][j] = Rover(i, j, i*(rows-1), j*(cols-1), 0)
            start_pos = Node(i*(rows-1), j*(cols-1))
            update_rover_position(rover[i][j], start_pos, True)

    # Initialize flag positions on grid (half way between the groups)
    set_flag_position(0, 0, int(cols / 2))
    set_flag_position(1, rows-1, int(cols / 2))

    # Add a textbox showing log of events on right of the grid
    log_text = Text(root, height=30, width=50, bg="black", fg="white", font=("Arial", 16))
    log_text.grid(row=0, column=cols+1, rowspan=rows, padx=50, pady=10, sticky=N+S+E+W)
    log_text.insert(END, "Event Log:\n")

    # Start the main event loop
    root.mainloop()