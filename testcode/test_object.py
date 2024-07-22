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
    
    # Example of adding hashvalue to JSON attributes
    # message = {
    #     "found_button": False,
    #     "pressed_button": False,
    #     "found_flag": False,
    #     "captured_flag": False
    # }
    
    # m = hashlib.sha256()
    # m.update(json.dumps(message).encode())
    # h = m.hexdigest()  
    
    # auth_message = {
    #     "found_button": False,
    #     "pressed_button": False,
    #     "found_flag": False,
    #     "captured_flag": False,
    #     "hash_value": h
    # }
    
    # print(auth_message)
    
    # # remove key from auth_message
    # del auth_message["hash_value"]
    # m = hashlib.sha256()
    # m.update(json.dumps(auth_message).encode())
    # h = m.hexdigest()  
    
    # print(h)