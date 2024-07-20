import time
import paho.mqtt.client as paho
import threading
import socket
from rover import Rover

def main():
    
    # Start the ESP32 serial connection
    threading.Thread(target=serialcomm).start()
    
    # Start the vSLAM thread
    threading.Thread(target=vslam).start()
    
    # Start the OpenCV thread
    threading.Thread(target=opencv).start()
    
    # Start pathfinder
    #threading.Thread(target=pathfinder).start()
    threading.Thread(target=pathfinder_simulated).start()
    
    # Start publishing rover state every 1 second
    #threading.Thread(target=publish_data).start()
    
    while True:
        pass
    
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     print("Shutting down")
    #finally:
        # Cleanup
        # Disconnect from MQTT broker
        #stop_mqtt_connection()
        #exit()
    
    #print(rover.to_json())

def start_mqtt_connection():
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    client.on_message = parse_message
    client.subscribe("team0/group1", 1)
    client.connect("localhost", 1883, 60)   
    client.loop_start()
    return client

def stop_mqtt_connection():
    client.loop_stop()
    client.disconnect()

def parse_message(client, userdata, message):
    # Update rover state based on received message
    # global rover
    # e.g. rover.c = message['c']
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}' with QoS {message.qos}")

# Stub
def serialcomm():
    pass

# Stub
def vslam():
    pass

# Stub
def opencv():
    pass

# Stub
def pathfinder():
    pass

# Stub
def publish_data():
    while True:
        msg = client.publish("team0/group1", "Hello, world!", 1)
        msg.wait_for_publish()
        print("Published message")
        time.sleep(1)

def pathfinder_simulated():
    host = socket.gethostname() # 192.168.0.2
    port = 7777  

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    while True:
        data = client_socket.recv(1024).decode()
        if data is not None:
            print("Received from server: " + str(data))

if __name__ == "__main__":
    # Create internal state
    rover = Rover(0, 0, 4, 5, 100)
    client = start_mqtt_connection()
    main()