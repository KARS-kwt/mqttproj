
import paho.mqtt.client as paho
import config

class MQTTClientConnector:
    
    def __init__(self, client_id):
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_publish = self.on_publish
        self.client.user_data_set([])
        self.client.connect(config.BROKER_LOCAL_ADDRESS, config.BROKER_PORT, config.BROKER_KEEP_ALIVE)
        self.client.loop_start()

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}")
        else:
            # we should always subscribe from on_connect callback to be sure
            # our subscribed is persisted across reconnections.
            print(f"Connected with result code {reason_code}")
            client.subscribe("test_topic")
    

    def on_message(self, client, userdata, message):
        userdata.append(message.payload)
        print(f"Received message '{str(message.payload)}' on topic '{message.topic}' with QoS {message.qos}")

    def subscribe(self, topic):
        self.client.subscribe(topic, 1)
    
    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        # Since we subscribed only for a single channel, reason_code_list contains
        # a single entry
        if reason_code_list[0].is_failure:
            print(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
        # Be careful, the reason_code_list is only present in MQTTv5.
        # In MQTTv3 it will always be empty
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
        else:
            print(f"Broker replied with failure: {reason_code_list[0]}")
        client.disconnect()

    def publish(self, topic, payload):
        self.client.publish(topic, payload, 1)
    
    def on_publish(self, client, userdata, mid):
        print(f"Published message with mid {mid}")      

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()