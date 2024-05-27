# import required packages 
import json
import config
from enum import Enum
from map_pathfinder import Node, Occupant

class Mode(Enum):
    EXPLORING = 1
    LOOKING_FOR_BUTTON = 2
    HEADING_TO_BUTTON = 3
    LOOKING_FOR_FLAG = 4
    HEADING_TO_FLAG = 5

class ArmStatus(Enum):
    RETRACTED = 1
    EXTENDED = 2

class Rover:  

    #TODO: Refactor rover variables into constructor

    # Rover's team ID
    team_id = -1
    group_id = -1

    # Rover's view of the environment 
    mode = Mode.HEADING_TO_FLAG        
    team_flag_in_base = True                               
    opp_flag_in_base =  [True for _ in range(config.NUM_TEAMS - 1)]

    # Rover's orientation (in degrees)
    orientation = 0

    # Vision status
    camera_on = True 
    wheels_on = True
    
    # Arm status
    arm_status = ArmStatus.RETRACTED
    
    # Constructor
    def __init__(self, team_id, group_id, r, c, orientation):
        self.team_id = team_id
        self.group_id = group_id
        self.r = r
        self.c = c
        self.orientation = orientation

        # Initialize the rover's gridview with unknown occupants
        self.my_grid = [[Node(r, c) for c in range(config.GRID_COLS)] for r in range(config.GRID_ROWS)]
        self.my_grid[r][c].visited = True
        self.my_obstacles = set()
    
    def update_occupant(self, r, c, type):
        self.my_grid[r][c].occupant = type
        if type != Occupant.EMPTY:
            self.my_obstacles.add((r, c))
    
    def get_all_obstacles(self):
        return self.my_obstacles

    # Print the grid with equal spacing
    def print_grid(self):
        for row in self.my_grid:
            for cell in row:
                print(f"{cell.occupant.value:3}", end="")
            print()
        print()

    # Convert to JSON
    def to_json(self):
        return json.dumps(self.__dict__)

    # Convert from JSON
    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        return Rover(json_dict['r'], json_dict['c'])

