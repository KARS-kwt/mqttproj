import atexit
from tkinter import *
import os
import threading
import multiprocessing
import uvicorn
import socket
import Pmw
import config
import random
from PIL import Image,ImageTk
from nav_unit import Node, Occupant, a_star
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
            if cell.occupant == Occupant.REDBUTTON:
                label.config(bg="red", image=blank)
            if cell.occupant == Occupant.BLUEBUTTON:
                label.config(bg="blue", image=blank)

def create_start_button():
            
    # Create a button to start the simulation
    start_button = Button(root, text="Start Simulation", bg="green", fg="white", font=("Arial", 20), command=start_simulation)
    start_button.grid(row=rows, column=0, columnspan=int(cols/2))

    # Add tooltip for start button
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to start the simulation')

def create_reset_button():
            
    # Create a button to reset the simulation
    reset_button = Button(root, text="Reset", bg="blue", fg="white", font=("Arial", 20), command=initialize_simulation)
    reset_button.grid(row=rows, column=int(cols/2), columnspan=int(cols/2))

    # Add tooltip for start button
    reset_button_tt = Pmw.Balloon(root) 
    reset_button_tt.bind(reset_button,'Click here to reset the simulation')

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
    obs_added = 0
    while obs_added < num_rand_obstacles:
        r = random.randint(3, rows-3)
        c = random.randint(0, cols-1)
        if (r, c) not in obstacles:
            obs_added += 1
            obstacles.add((r, c))
    
    # Set the obstacles on the grid
    for obstacle in obstacles:
        grid[obstacle[0]][obstacle[1]].occupant = Occupant.OBSTACLE
    
    return obstacles

# Generate buttons for each team
def generate_buttons(buttons_per_team):
    
    buttons = set()
    
    buttons_added = 0
    while buttons_added < buttons_per_team * config.NUM_TEAMS:
        r = random.randint(3, rows-3)
        c = random.randint(0, cols-1)
        if grid[r][c].occupant == Occupant.EMPTY:
            if buttons_added % 2 == 0:
                grid[r][c].occupant = Occupant.BLUEBUTTON
            else:            
                grid[r][c].occupant = Occupant.REDBUTTON
            buttons_added += 1
            buttons.add((r, c))
            
    return buttons   

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
    
    if human_players:
        rover.socket.sendall(rover.to_json().encode())
    
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

# Move rover one step towards goal
def move_rover(rover):
    
    start = Node(rover.r, rover.c)
    path = None

    # Scan the environment for an unexplored area
    if rover.mode == Mode.EXPLORING:
        
        # TODO: This should be replaced by vSLAM or some other monocular vision odometry algorithm
        # Right now it naively assumes a panoramic (360-degree) FOV
        rover.scan(grid)
        
        # Check if found button
        # if rover.button1_loc:
        #     r, c = rover.button1_loc.r, rover.button1_loc.c
        #     update_log(f"Team {rover.team_id} - Rover {rover.group_id} has found Button 1\n")
        #     rover.mqtt_conn.publish(f"team{rover.team_id}/group{rover.group_id}/button", f"found at location ({r}, {c})")
        #     rover.mode = Mode.HEADING_TO_BUTTON
        #     return

        # Check if found opponent's flag
        if rover.opp_flag_loc:
            r, c = rover.opp_flag_loc.r, rover.opp_flag_loc.c
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has found the opponent's flag\n")
            #rover.mqtt_conn.publish(f"team{rover.team_id}/group{rover.group_id}/flag", f"found at location ({r}, {c})")
            rover.mode = Mode.HEADING_TO_FLAG
        else:
            # Go to the farthest unvisited cell
            path = rover.explore()
    
    if rover.mode == Mode.HEADING_TO_FLAG:
        goal = Node((1-rover.team_id) * (rows-1), int(cols / 2)) 
        #TODO: move this to rover
        path = a_star(rows, cols, start, goal, obstacles)
    
    # Update the rover position by moving one step along the path
    if path and len(path) > 1:
        r, c = path[1]    
        if grid[r][c].occupant == Occupant.REDFLAG and rover.team_id == 1:
            # Rover has captured the flag!
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has captured the flag\n")
            rover.mode = Mode.RETURNING_TO_BASE
            return
        if grid[r][c].occupant == Occupant.BLUEFLAG and rover.team_id == 0:
            # Rover has captured the flag!
            update_log(f"Team {rover.team_id} - Rover {rover.group_id} has captured the flag\n")
            rover.mode = Mode.RETURNING_TO_BASE
            return
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
    for i in range(config.NUM_TEAMS):
        for j in range(config.NUM_GROUPS):
            if rovers[i][j] is not None:
                move_rover(rovers[i][j])
                
    #move_rover(rovers[0][0])
    #move_rover(rovers[0][1])
    #move_rover(rovers[1][0])
    #move_rover(rovers[1][1])

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
    start_button.config(text="Pause Simulation", bg="red", command=stop_simulation)
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to pause the simulation')

def initialize_simulation():
    
    global timestamp, grid, buttons, obstacles, rovers, log_text
    timestamp = 0

    # Reset the grid
    grid = init_grid()
    obstacles = generate_obstacles(config.NUM_OBSTACLES)
    buttons = generate_buttons(2)
    draw_grid()
    
    # Add a textbox showing log of events on right of the grid
    log_text = Text(root, height=30, width=50, bg="black", fg="white", font=("Arial", 16))
    log_text.grid(row=0, column=cols, rowspan=rows+1, padx=50, pady=10, sticky=N+S+E+W)
    update_log("Welcome to the KARS Summer Camp 2024!\nEvent Log:\n", False)

    # Reset the flag positions
    set_flag_position(0, 0, int(cols / 2))
    set_flag_position(1, rows-1, int(cols / 2))
    
    # Reset the rovers
    if not human_players:
        for i in range(config.NUM_TEAMS):
            for j in range(config.NUM_GROUPS):
                if rovers[i][j]:
                    rovers[i][j].mqtt_conn.disconnect()
                rovers[i][j] = Rover(i, j, i*(rows-1), j*(cols-1), 0)
                rovers[i][j].start_connection()
                rovers[i][j].scan(grid)
                start_pos = Node(i*(rows-1), j*(cols-1))
                update_rover_position(rovers[i][j], start_pos, True)
                update_log(f"Team {i} - Rover {j} Deployed\n")
    else:
        socket_server = start_socket_server()
        for i in range(config.NUM_TEAMS):
            for j in range(config.NUM_GROUPS):
                threading.Thread(target=human_player, args=(socket_server, i, j)).start()

def start_socket_server():
    host = socket.gethostname() # 192.168.0.2
    port = 7777  

    server_socket = socket.socket()
    server_socket.bind((host, port)) 

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    return server_socket

def human_player(server_socket, i, j):
    conn, address = server_socket.accept()
    #print("Rover connected from: " + str(address))
    rovers[i][j] = Rover(i, j, i*(rows-1), j*(cols-1), 0)
    rovers[i][j].socket, rovers[i][j].address = conn, address
    rovers[i][j].scan(grid)
    start_pos = Node(i*(rows-1), j*(cols-1))
    update_rover_position(rovers[i][j], start_pos, True)
    update_log(f"Team {i} - Rover {j} Connected from " + str(address) + "\n")

if __name__ == "__main__":

    # Initialize the main window
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

    # Initialize the simulation
    human_players = True
    rovers = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    initialize_simulation()    
    create_start_button()
    create_reset_button()

    # Start the uvicorn server on a different child process (tkinter is not thread-safe)
    #p = multiprocessing.Process(target=uvicorn.run, kwargs={'app':'api:app'})
    #p.start()
    #atexit.register(p.kill)

    # Start the main event loop
    root.mainloop()