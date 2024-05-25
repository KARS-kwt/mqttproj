from tkinter import *
import Pmw
import ctypes as ct
import config
import random
from PIL import Image,ImageTk

def create_grid(rows, columns):

    # Create a grid of Label objects
    for i in range(rows):
        for j in range(columns):
            label = Label(root, height=100, width=100, relief=RAISED, borderwidth=2, image=blank)
            label.grid(row=i, column=j)
    
    # Create a button to start the simulation
    start_button = Button(root, text="Start Simulation", bg="green", fg="white", command=start_simulation)
    start_button.grid(row=rows, column=0, columnspan=columns)

    # Add tooltip for start button
    start_button_tt = Pmw.Balloon(root) 
    start_button_tt.bind(start_button,'Click here to start the simulation')

def set_rover_position(team_id, rover_id, r, c):

    # Clear the previous position
    if rover[team_id][rover_id] is not None:
        label = Label(root, height=100, width=100, relief=RAISED, borderwidth=2, image=blank)
        label.grid(row=rover[team_id][rover_id].get("r"), column=rover[team_id][rover_id].get("c"))
        rover[team_id][rover_id] = None

    # Set the new position
    rover[team_id][rover_id] = {"r": r, "c": c}
    label = Label(root, height=100, width=100, relief=RAISED, borderwidth=2, image=blank)
    label.grid(row=r, column=c)
    if team_id == 0:
        label.config(image=red_image, height=100, width=100)
    else:
        label.config(image=blue_image, height=100, width=100)
    
    # Add tooltip for rover
    rover_tt = Pmw.Balloon(root)
    rover_tt.bind(label, f"Team {team_id} - Rover {rover_id}")

def move_rover(team_id, rover_id, direction):
    r = rover[team_id][rover_id].get("r")
    c = rover[team_id][rover_id].get("c")
    if direction == "up":
        # Check if the rover is not at the top edge
        if r == 0:
            return
        r = r - 1
    elif direction == "down":
        # Check if the rover is not at the bottom edge
        if r == config.GRID_ROWS - 1:
            return
        r = r + 1
    elif direction == "left":
        # Check if the rover is not at the left edge
        if c == 0:
            return
        c = c - 1
    elif direction == "right":
        # Check if the rover is not at the right edge
        if c == config.GRID_COLS - 1:
            return
        c = c + 1
    set_rover_position(team_id, rover_id, r, c)

def start_simulation():

    # Choose randomly between 4 strings
    directions = ["up", "down", "left", "right"]

    # Generate 4 random directions
    random_direction = [random.choice(directions) for _ in range(4)]

    # Move the rovers
    move_rover(0, 0, random_direction[0])
    move_rover(0, 1, random_direction[1])
    move_rover(1, 0, random_direction[2])
    move_rover(1, 1, random_direction[3])

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

    # Initialize rover parameters
    rover = [[None for _ in range(2)] for _ in range(config.NUM_TEAMS)]
    blank = PhotoImage()
    red_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/redrobot.gif").resize((100, 100)))
    blue_image = ImageTk.PhotoImage(Image.open("mqtt_clients/images/bluerobot.gif").resize((100, 100)))

    # Create the grid
    create_grid(config.GRID_ROWS, config.GRID_COLS)

    # Initialize team positions on grid
    set_rover_position(0, 0, 0, 0)
    set_rover_position(0, 1, 0, config.GRID_COLS-1)
    set_rover_position(1, 0, config.GRID_ROWS-1, 0)
    set_rover_position(1, 1, config.GRID_ROWS-1, config.GRID_COLS-1)

    # Start the main event loop
    root.mainloop()