import sys
import os
import hashlib
import paho.mqtt.client as paho

child_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(child_dir, '..'))
sys.path.append(parent_dir)

import config as conf
from rover import *

client = paho.Client(paho.CallbackAPIVersion.VERSION2)

if client.connect(conf.BROKER_NETWORK_ADDRESS, 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)
    
client.loop_start()

my_rover = Rover(0, 1, 4, 5, 100)

# Compute the hash of the rover object
key = "12345"
hash_object = hashlib.sha256(my_rover.to_json().encode())
hash_object.update(key.encode())
hash_value = hash_object.hexdigest()
print(hash_value)

msg = client.publish("team1/group1", my_rover.to_json(), 1)
msg.wait_for_publish()

client.loop_stop()
client.disconnect()
