import tkinter as tk
import sys
import json
import paho.mqtt.client as paho

def publish_message(signal):
    msg = client.publish("team1/group1", json.dumps(signal), 1)
    msg.wait_for_publish(1)

def message_handling(client, userdata, msg:paho.MQTTMessage):
    payload = json.loads(msg.payload)
    if "found_button" in payload:
        if payload["found_button"]:
            canvas.itemconfig(status1, fill="green")
        else:
            canvas.itemconfig(status1, fill="red")
    if "pressed_button" in payload:
        if payload["pressed_button"]:
            canvas.itemconfig(status2, fill="green")
        else:
            canvas.itemconfig(status2, fill="red")
    if "found_flag" in payload:
        if payload["found_flag"]:
            canvas.itemconfig(status3, fill="green")
        else:
            canvas.itemconfig(status3, fill="red")
    if "captured_flag" in payload:
        if payload["captured_flag"]:
            canvas.itemconfig(status4, fill="green")
        else:
            canvas.itemconfig(status4, fill="red")
                    
    root.update()

def client_disconnected(client, userdata, rc):
    client.loop_stop()
    print(f"Disconnected with result code: {rc}")

if __name__ == "__main__":

    root = tk.Tk()  # Set Tk instance

    canvas = tk.Canvas(root, width=750, height=200)
    canvas.pack()

    status1 = canvas.create_oval(50, 50, 100, 100)
    label1 = canvas.create_text(75, 120, text="Found Button", font=("Arial", 12))

    status2 = canvas.create_oval(250, 50, 300, 100)
    label2 = canvas.create_text(275, 120, text="Pressed Button", font=("Arial", 12))

    status3 = canvas.create_oval(450, 50, 500, 100)
    label3 = canvas.create_text(475, 120, text="Found Flag", font=("Arial", 12))

    status4 = canvas.create_oval(650, 50, 700, 100)
    label4 = canvas.create_text(675, 120, text="Captured Flag", font=("Arial", 12))

    my_button1 = tk.Button(root, text="Send Found Button Signal", command=lambda: publish_message({"found_button": True}))
    my_button2 = tk.Button(root, text="Send Pressed Button Signal", command=lambda: publish_message({"pressed_button": True}))
    my_button3 = tk.Button(root, text="Send Found Flag Signal", command=lambda: publish_message({"found_flag": True}))
    my_button4 = tk.Button(root, text="Send Captured Flag Signal", command=lambda: publish_message({"captured_flag": True}))
    my_button1.pack()
    my_button2.pack()
    my_button3.pack()
    my_button4.pack()
    
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    client.on_message = message_handling
    client.on_disconnect = client_disconnected
    
    if client.connect("127.0.0.1", 1883, 60) != 0:
        print("Couldn't connect to the mqtt broker")
        sys.exit(1)
    
    try:
        client.loop_start()   
        client.subscribe("team1/group1", 1)    
        print("Press CTRL+C to exit...") 
    except Exception as e:
        print(e)     

    root.mainloop()