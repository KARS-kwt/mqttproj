import json 
import hashlib

class TestObject:  
    
    def __init__(self, attr):
        if attr is not None:
            for key, value in attr.items():
                setattr(self, key, value)
        
    # Convert to JSON (for MQTT messages)
    def to_json(self):
        return json.dumps(self.__dict__)

    # Convert from JSON
    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        return TestObject(json_dict)

    def computeHash(self, message):
        m = hashlib.sha3_512()
        m.update(message)
        h = m.hexdigest()      
        return h 
    
    
    # JSON attributes
    attributes = {
        "orientation" : 110,
        "message" : "",
        "armstatus" : 1,
        "flag_location": [10, 20],
        "is_button_pressed" : False
    }