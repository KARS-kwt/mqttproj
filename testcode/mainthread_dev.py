import paho.mqtt.client as paho
import threading
import time
from rover import Rover

def main():
    
    threading.Thread(target=publish_data).start()
    
    threading.Thread(target=vslam).start()
    
    threading.Thread(target=yolo).start()
        
    while True:
        pass
    
def start_mqtt():
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    client.on_message = parse_message
    client.subscribe("team0/group1", 1)
    client.connect("192.168.0.2", 1883, 60)   
    client.loop_start()
    return client

def parse_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}' with QoS {message.qos}")
   
def publish_data():
    while True:
        msg = client.publish("team0/group2", "Hello World", 1) 
        msg.wait_for_publish()
        print("I published the message")
        time.sleep(1)
        
def vslam():
    pass

# Will later be replaced by the navigation unit
def yolo():
    pass

if __name__ == "__main__":
    client = start_mqtt()
    state = Rover(0, 0, 12, 30)
    main()