# import required packages 
import json 
import config

class Rover:  

    # Rover's view of the environment
    team_flag_in_base = True                               
    opp_flag_in_base =  [True for _ in range(config.NUM_TEAMS - 1)]

    # Rover's grid position
    x_pos = 0
    y_pos = 0

    # Rover's orientation (in degrees)
    orientation = 0

    # Vision status
    camera_on = True 
    wheels_on = True
    
    # Arm status
    arm_status = "retracted"
    
    # Constructor
    def __init__(self, team_id, group_id, x, y):
        self.team_id = team_id,
        self.group_id = group_id,
        self.x = x
        self.y = y

    # Convert to JSON
    def to_json(self):
        return json.dumps(self.__dict__)

    # Convert from JSON
    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        return Rover(json_dict['x'], json_dict['y'])
