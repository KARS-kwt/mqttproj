import sys
import os
import json 
import paho.mqtt.client as paho

child_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(child_dir, '..'))
sys.path.append(parent_dir)

from rover import Rover
import config as conf

def message_handling(client, userdata, msg:paho.MQTTMessage):
    payload = Rover.from_json(msg.payload.decode())
    print(f"{msg.topic}: {payload}")            
    

client = paho.Client(paho.CallbackAPIVersion.VERSION2)
client.on_message = message_handling

if client.connect(conf.BROKER_NETWORK_ADDRESS, 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

client.subscribe("test_topic", 1)

try:
    print("Press CTRL+C to exit...")
    client.loop_forever()           
    # Alternatively the non-blocking client.loop_start() can be used
    # but the finally block will need to be removed and an event handler
    # for the on_disconnect event will need to be added to disconnect the client
except Exception as e:
    print("Caught an Exception, something went wrong...")
    print(e) 
finally:
    print("Disconnecting from the MQTT broker")
    client.disconnect()