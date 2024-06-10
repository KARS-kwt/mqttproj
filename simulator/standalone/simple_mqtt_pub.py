import sys
import os
import paho.mqtt.client as paho

child_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(child_dir, '..'))
sys.path.append(parent_dir)
import config as conf

client = paho.Client(paho.CallbackAPIVersion.VERSION2)

if client.connect(conf.BROKER_NETWORK_ADDRESS, 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)

client.publish("test_topic", "Hi, paho mqtt client works fine!", 0)
client.disconnect()