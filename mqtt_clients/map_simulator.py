from tkinter import *
import Pmw
import config
import random
from PIL import Image,ImageTk
from map_pathfinder import Node, a_star

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

    # Add a textbox showing log of events on right of the grid
    log_text = Text(root, height=30, width=50, bg="black", fg="white", font=("Arial", 16))
    log_text.grid(row=0, column=columns+1, rowspan=rows, padx=50, pady=10, sticky=N+S+E+W)
    log_text.insert(END, "Event Log:\n")


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
        label.config(image=red_flag, height=ch, width=cw)
    else:
        label.config(image=blue_flag, height=ch, width=cw)
    
    # Add tooltip for flag
    flag_tt = Pmw.Balloon(root)
    flag_tt.bind(label, f"Team {team_id} - Flag")

def set_rover_position(team_id, rover_id, r, c):

    # Clear the previous position
    if rover[team_id][rover_id] is not None:
        label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
        label.grid(row=rover[team_id][rover_id].get("r"), column=rover[team_id][rover_id].get("c"))
        rover[team_id][rover_id] = None

    # Set the new position
    rover[team_id][rover_id] = {"r": r, "c": c}
    label = Label(root, height=ch, width=cw, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=r, column=c)
    if team_id == 0:
        label.config(image=red_image, height=ch, width=cw)
    else:
        label.config(image=blue_image, height=ch, width=cw)
    
    # Add tooltip for rover
    rover_tt = Pmw.Balloon(root)
    rover_tt.bind(label, f"Team {team_id} - Rover {rover_id}")

def move_rover(team_id, rover_id):
    r = rover[team_id][rover_id].get("r")
    c = rover[team_id][rover_id].get("c")

    # Apply A* algorithm to reach the flag
    grid = [[Node(r, c) for c in range(cols)] for r in range(rows)]
    start = grid[r][c]
    goal = grid[rows-1][int(config.GRID_COLS / 2)]
    path = a_star(start, goal, grid, obstacles)
    if path:
        r, c = path[1]    
    set_rover_position(team_id, rover_id, r, c)

def start_simulation():

    # Move the rovers synchronously
    move_rover(0, 0)
    #move_rover(0, 1)
    #move_rover(1, 0)
    #move_rover(1, 1)

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
    rover = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    blank = PhotoImage()
    red_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redrobot.png").resize((ch, cw)))
    blue_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/bluerobot.png").resize((ch,cw)))
    red_flag = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redflag.png").resize((ch, cw)))
    blue_flag = ImageTk.PhotoImage(Image.open("mqtt_clients/images/blueflag.png").resize((ch, cw)))

    # Draw the grid
    draw_grid(rows, cols)
    obstacles = generate_obstacles(20)

    # Initialize team positions on grid
    set_rover_position(0, 0, 0, 0)
    set_rover_position(0, 1, 0, config.GRID_COLS-1)
    set_rover_position(1, 0, config.GRID_ROWS-1, 0)
    set_rover_position(1, 1, config.GRID_ROWS-1, config.GRID_COLS-1)

    # Initialize flag positions on grid (half way between the groups)
    set_flag_position(0, 0, int(config.GRID_COLS / 2))
    set_flag_position(1, config.GRID_ROWS-1, int(config.GRID_COLS / 2))

    # Start the main event loop
    root.mainloop()