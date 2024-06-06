# import required packages 
import json
import config
from mqtt_connector import MQTTClientConnector
from enum import Enum
from map_pathfinder import Node, Occupant, manhattan_distance, a_star

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
        self.mqtt_conn = MQTTClientConnector(f"rover_{team_id}_{group_id}")
        
        # Initialize rover equipment status
        self.camera_status = CameraStatus.OFF
        self.wheel_status = WheelStatus.STOPPED
        self.arm_status = ArmStatus.RETRACTED

        # Initialize the rover's gridview with unknown occupants
        self.my_grid = [[Node(r, c) for c in range(config.GRID_COLS)] for r in range(config.GRID_ROWS)]
        self.my_grid[r][c].visited = True
        self.my_obstacles = set()
        self.team_flag_in_base = True                               
        self.opp_flag_in_base =  [True for _ in range(config.NUM_TEAMS - 1)]
    
    # Update the rover's grid view with the new occupant information
    def update_occupant(self, r, c, type, rover_ref=None):
        self.my_grid[r][c].occupant = type
        if type != Occupant.EMPTY:
            self.my_obstacles.add((r, c))
        if type == Occupant.ROVER:
            self.my_grid[r][c].occupant_ref = rover_ref
    
    # Retrieves the set of all obstacles in the rover's grid view
    def get_all_obstacles(self):
        return self.my_obstacles

    # Print the rover's view of the grid
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
            if nr == r: # Skip the current cell
                continue   
            if grid[nr][c].occupant != Occupant.EMPTY:  
                break
        for nr in range(r, -1, -1): # UP
            self.update_occupant(nr, c, grid[nr][c].occupant, grid[nr][c].occupant_ref)
            if nr == r:
                continue   
            if grid[nr][c].occupant != Occupant.EMPTY:  
                break
        for nc in range(c, len(grid[0])): # RIGHT
            if nc == c:
                continue 
            self.update_occupant(r, nc, grid[r][nc].occupant, grid[r][nc].occupant_ref)
            if grid[r][nc].occupant != Occupant.EMPTY:
                break
        for nc in range(c, -1, -1): # LEFT
            if nc == c:
                continue 
            self.update_occupant(r, nc, grid[r][nc].occupant, grid[r][nc].occupant_ref)
            if grid[r][nc].occupant != Occupant.EMPTY:
                break

        # Scan the top-left diagnoal from the rover (except current cell)
        for i in range(1, min(r, c) + 1):
            self.update_occupant(r-i, c-i, grid[r-i][c-i].occupant, grid[r-i][c-i].occupant_ref)
            if grid[r-i][c-i].occupant != Occupant.EMPTY:
                break
        
        # Scan the top-right diagnoal from the rover (except current cell)
        for i in range(1, min(r, len(grid[0])-1-c) + 1):
            self.update_occupant(r-i, c+i, grid[r-i][c+i].occupant, grid[r-i][c+i].occupant_ref)
            if grid[r-i][c+i].occupant != Occupant.EMPTY:
                break

        # Scan the bottom-left diagnoal from the rover (except current cell)
        for i in range(1, min(len(grid)-1-r, c) + 1):
            self.update_occupant(r+i, c-i, grid[r+i][c-i].occupant, grid[r+i][c-i].occupant_ref)
            if grid[r+i][c-i].occupant != Occupant.EMPTY:
                break
        
        # Scan the bottom-right diagnoal from the rover (except current cell)
        for i in range(1, min(len(grid)-1-r, len(grid[0])-1-c) + 1):
            self.update_occupant(r+i, c+i, grid[r+i][c+i].occupant, grid[r+i][c+i].occupant_ref)
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
        return json.dumps(self.__dict__)

    # Convert from JSON
    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        return Rover(json_dict['r'], json_dict['c'])


