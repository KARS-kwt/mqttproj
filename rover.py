# import required packages 
import json
import requests
import config
from comm_unit import MQTTClientConnector
from enum import Enum
from nav_unit import Node, Occupant, manhattan_distance, a_star

class Mode(Enum):
    EXPLORING = 1
    LOOKING_FOR_BUTTON = 2
    HEADING_TO_BUTTON = 3
    LOOKING_FOR_FLAG = 4
    HEADING_TO_FLAG = 5
    RETURNING_TO_BASE = 6

class CameraStatus(Enum):
    ON = 1
    OFF = 2

class ArmStatus(Enum):
    RETRACTED = 1
    EXTENDED = 2

class WheelStatus(Enum):
    STOPPED = 1
    MOVING = 2

class Rover:  
    
    # Constructor
    def __init__(self, team_id, group_id, r, c, orientation):
        self.team_id = team_id
        self.group_id = group_id
        self.r = r
        self.c = c
        self.orientation = orientation
        self.mode = Mode.EXPLORING  
        
        # Socket info (for human players only)
        self.socket = None
        self.address = None
        
        # Initialize rover equipment status
        self.camera_status = CameraStatus.OFF
        self.wheel_status = WheelStatus.STOPPED
        self.arm_status = ArmStatus.RETRACTED

        # Initialize the rover's gridview with unknown occupants
        self.my_grid = [[Node(r, c) for c in range(config.GRID_COLS)] for r in range(config.GRID_ROWS)]
        self.my_grid[r][c].visited = True
        self.my_obstacles = set()
        self.team_flag_in_base = True                               
        self.opp_flag_loc = None
        self.button1_loc = None
        self.button2_loc = None
    
    # Start the MQTT connection and subscribe to other groups' topics (in the same team)
    def start_connection(self):
        self.mqtt_conn = MQTTClientConnector(f"rover_{self.team_id}_{self.group_id}", parse_message)
        for team in range(config.NUM_TEAMS):
            for group in range(config.NUM_GROUPS):
                if team == self.team_id and group != self.group_id:
                    self.mqtt_conn.subscribe(f"team{team}/group{group}/#")
    
    # Update the rover's grid view with the new occupant information
    def update_occupant(self, r, c, type, rover_ref=None):
        self.my_grid[r][c].occupant = type
        if type != Occupant.EMPTY:
            self.my_obstacles.add((r, c))
        if type == Occupant.ROVER:
            self.my_grid[r][c].occupant_ref = rover_ref
    
    def update_flag_found(self, r, c):
        if self.my_grid[r][c].occupant == Occupant.BLUEFLAG and self.team_id == 0:
            self.opp_flag_loc = self.my_grid[r][c]
        if self.my_grid[r][c].occupant == Occupant.REDFLAG and self.team_id == 1:
            self.opp_flag_loc = self.my_grid[r][c]
    
    def update_button_found(self, r, c):
        if (
            (self.my_grid[r][c].occupant == Occupant.REDBUTTON and self.team_id == 0) 
            or  
            (self.my_grid[r][c].occupant == Occupant.BLUEBUTTON and self.team_id == 1)
        ):
            if self.button1_loc == None:
                self.button1_loc = self.my_grid[r][c]
            else: 
                if self.button2_loc == None:
                    self.button2_loc = self.my_grid[r][c]         
    
    # Retrieves the set of all obstacles in the rover's grid view
    def get_all_obstacles(self):
        return self.my_obstacles

    # Print the rover's view of the grid in console (for debugging)
    def print_grid(self):
        for row in self.my_grid:
            for cell in row:
                print(f"{cell.occupant.value:3}", end="")
            print()
        print()

    # Used to update rover's view of the environment using the real grid (acts like a chess queen)
    def scan(self, grid):

        r, c = self.r, self.c
        
        # Reset the rover's perspective of all rover positions (since they move around)
        for row in self.my_grid:
            for cell in row:
                if cell.occupant == Occupant.ROVER:
                    cell.occupant = Occupant.EMPTY
                    cell.occupant_ref = None

        # Scan the grid by looking at all cells in the same row and/or column as the rover (cannot see beyond obstacles)
        for nr in range(r, len(grid)): # DOWN         
            self.update_occupant(nr, c, grid[nr][c].occupant, grid[nr][c].occupant_ref)
            self.update_flag_found(nr, c)
            self.update_button_found(nr, c)
            if nr == r: # Skip the current cell
                continue   
            if grid[nr][c].occupant != Occupant.EMPTY:  
                break
        for nr in range(r, -1, -1): # UP
            self.update_occupant(nr, c, grid[nr][c].occupant, grid[nr][c].occupant_ref)
            self.update_flag_found(nr, c)
            self.update_button_found(nr, c)
            if nr == r:
                continue   
            if grid[nr][c].occupant != Occupant.EMPTY:  
                break
        for nc in range(c, len(grid[0])): # RIGHT
            if nc == c:
                continue 
            self.update_occupant(r, nc, grid[r][nc].occupant, grid[r][nc].occupant_ref)
            self.update_flag_found(r, nc)
            self.update_button_found(r, nc)
            if grid[r][nc].occupant != Occupant.EMPTY:
                break
        for nc in range(c, -1, -1): # LEFT
            if nc == c:
                continue 
            self.update_occupant(r, nc, grid[r][nc].occupant, grid[r][nc].occupant_ref)
            self.update_flag_found(r, nc)
            self.update_button_found(r, nc)
            if grid[r][nc].occupant != Occupant.EMPTY:
                break

        # Scan the top-left diagnoal from the rover (except current cell)
        for i in range(1, min(r, c) + 1):
            self.update_occupant(r-i, c-i, grid[r-i][c-i].occupant, grid[r-i][c-i].occupant_ref)
            self.update_flag_found(r-i, c-i)
            self.update_button_found(r-i, c-i)
            if grid[r-i][c-i].occupant != Occupant.EMPTY:
                break
        
        # Scan the top-right diagnoal from the rover (except current cell)
        for i in range(1, min(r, len(grid[0])-1-c) + 1):
            self.update_occupant(r-i, c+i, grid[r-i][c+i].occupant, grid[r-i][c+i].occupant_ref)
            self.update_flag_found(r-i, c+i)
            self.update_button_found(r-i, c+i)
            if grid[r-i][c+i].occupant != Occupant.EMPTY:
                break

        # Scan the bottom-left diagnoal from the rover (except current cell)
        for i in range(1, min(len(grid)-1-r, c) + 1):
            self.update_occupant(r+i, c-i, grid[r+i][c-i].occupant, grid[r+i][c-i].occupant_ref)
            self.update_flag_found(r+i, c-i)
            self.update_button_found(r+i, c-i)
            if grid[r+i][c-i].occupant != Occupant.EMPTY:
                break
        
        # Scan the bottom-right diagnoal from the rover (except current cell)
        for i in range(1, min(len(grid)-1-r, len(grid[0])-1-c) + 1):
            self.update_occupant(r+i, c+i, grid[r+i][c+i].occupant, grid[r+i][c+i].occupant_ref)
            self.update_flag_found(r+i, c+i)
            self.update_button_found(r+i, c+i)
            if grid[r+i][c+i].occupant != Occupant.EMPTY:
                break
    
    def explore(self):
        
        start = Node(self.r, self.c)
        
        # Set the goal to be the farthest unexplored cell
        max_distance = 0
        goal = None
        for row in self.my_grid:
            for cell in row:
                if not cell.visited and cell.occupant == Occupant.UNKNOWN:
                    distance = manhattan_distance(start, cell)
                    if distance > max_distance:
                        max_distance = distance
                        goal = cell

        rows = len(self.my_grid)
        cols = len(self.my_grid[0])

        # Find a path to that frontier
        path = a_star(rows, cols, start, goal, self.get_all_obstacles())
        
        return path

    # Convert to JSON (for MQTT messages)
    def to_json(self):
        seralizableDict = {}
        seralizableDict['team_id'] = self.team_id
        seralizableDict['group_id'] = self.group_id
        seralizableDict['r'] = self.r
        seralizableDict['c'] = self.c
        seralizableDict['orientation'] = self.orientation
        return json.dumps(seralizableDict)

    # Convert from JSON
    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        teammember = Rover(
            json_dict['team_id'],
            json_dict['group_id'],
            json_dict['r'], 
            json_dict['c'],
            json_dict['orientation'],
        )
        return teammember

def parse_message(client, userdata, message):
    """
    The default callback called when a message is received.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        message (paho.mqtt.client.MQTTMessage): The received message.
    """
    userdata.append(message.payload)
    print(f"Received message '{str(message.payload)}' on topic '{message.topic}' with QoS {message.qos}")

def get_posts():
    # Define the API endpoint URL
    url = 'https://jsonplaceholder.typicode.com/posts'

    try:
        # Make a GET request to the API endpoint using requests.get()
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        # Handle any network-related errors or exceptions
        print('Error:', e)
        return None
    finally:
        # Close the response
        response.close()


