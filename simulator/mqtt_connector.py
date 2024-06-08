
import config
import paho.mqtt.client as paho
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 


class MQTTClientConnector:
    """
    A class representing an MQTT client connector.

    Args:
        client_id (str): The client ID for the MQTT client.
        message_handler (Callable): The message handler to call when a message is received.
        version (int, optional): The MQTT protocol version. Defaults to 3.
        use_tls (bool, optional): Whether to use TLS for secure communication. Defaults to False.
        trans (str, optional): The transport protocol to use. Defaults to "tcp" (port 1883). Can be "websockets" to run on port 80/443
    """

    def __init__(self, client_id, message_handler = None, version=3, use_tls=False, trans="tcp"):
        """
        Initializes the MQTTClientConnector.

        Args:
            client_id (str): The client ID for the MQTT client.
            version (int, optional): The MQTT protocol version. Defaults to 3.
            use_tls (bool, optional): Whether to use TLS for secure communication. Defaults to False.
            trans (str, optional): The transport protocol to use. Defaults to "tcp". Can be "websockets" to run on port 80/443
        """
        
        if version == 3:
            self.client = paho.Client(paho.CallbackAPIVersion.VERSION2, 
                                      client_id, 
                                      transport=trans, 
                                      protocol=paho.MQTTv311, 
                                      clean_session=True)  
        if version == 5:
            self.client = paho.Client(paho.CallbackAPIVersion.VERSION2, 
                                      client_id, 
                                      transport=trans, 
                                      protocol=paho.MQTTv5)
        
        # Client Authentification and TLS setup
        if use_tls:
            self.client.username_pw_set(config.USERNAME, config.PASSWORD)
            # If certfile and keyfile are not None then they will be used as client information for TLS based
            # authentication and authorization (depends on broker setup). cert_reqs makes it mandatory that the 
            # broker has a valid certificate.
            self.client.tls_set(certfile=None,
                                keyfile=None,
                                cert_reqs=paho.ssl.CERT_REQUIRED)

        # Set the callbacks
        self.client.on_connect = on_connect
        if message_handler is not None:
            self.client.on_message = message_handler                # Custom message handler
        else:
            self.client.on_message = on_message                     # Default message handler
        self.client.on_subscribe = on_subscribe
        self.client.on_unsubscribe = on_unsubscribe
        self.client.on_publish = on_publish
        
        # Initialize user data to store received messages in the callbacks
        self.client.user_data_set([])
 
        if version == 3:
            self.client.connect(config.BROKER_LOCAL_ADDRESS, 
                                config.BROKER_PORT, 
                                config.BROKER_KEEP_ALIVE)
        
        if version == 5:
            properties=Properties(PacketTypes.CONNECT)
            properties.SessionExpiryInterval=30*60 # in seconds
            self.client.connect(config.BROKER_LOCAL_ADDRESS, 
                                config.BROKER_PORT, 
                                config.BROKER_KEEP_ALIVE,
                                clean_start=paho.MQTT_CLEAN_START_FIRST_ONLY,
                                properties=properties)
        
        # Asynchronous listening for messages on a different thread to avoid blocking the main thread
        # Thread will loop forever until disconnect is called
        self.client.loop_start()

    def subscribe(self, topic):
        """
        Subscribes to an MQTT topic with QoS 1.

        Args:
            topic (str): The topic to subscribe to.
        """
        self.client.subscribe(topic, 1)

    def publish(self, topic, payload):
        """
        Publishes a message to an MQTT topic with QoS 1.

        Args:
            topic (str): The topic to publish to.
            payload (str): The message payload.
        """
        properties=Properties(PacketTypes.PUBLISH)
        properties.MessageExpiryInterval=30
        msg_info = self.client.publish(topic, payload, 1, properties=properties)  

        # Block until publish has been acknowledged. This is useful for ensuring that the message has been sent.
        # Once done, on_publish callback will be called
        msg_info.wait_for_publish()

    def disconnect(self):
        """
        Disconnects the MQTT client. This will also stop the loop started in the constructor.
        """
        self.client.disconnect()
        self.client.loop_stop()     # Not really needed, but good practice
    

# MQTT Client Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    """
    The callback called when the client connects to the MQTT broker.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        flags (dict): The flags associated with the connection.
        reason_code (paho.mqtt.packettypes.ReasonCode): The reason code for the connection.
        properties (paho.mqtt.properties.Properties): The properties associated with the connection.
    """
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}")
    else:
        print(f"{client._client_id} connected with result code {reason_code}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    """
    The callback called when a subscribe request has completed.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        mid (int): The message ID of the subscribe request.
        reason_code_list (List[paho.mqtt.packettypes.ReasonCode]): The reason codes for the subscriptions.
        properties (paho.mqtt.properties.Properties): The properties associated with the subscribe request.
    """
    # Since we subscribed only for a single channel, reason_code_list contains a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected your subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    """
    The callback called when an unsubscribe request has completed.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        mid (int): The message ID of the unsubscribe request.
        reason_code_list (List[paho.mqtt.packettypes.ReasonCode], optional): The reason codes for the unsubscriptions.
        properties (paho.mqtt.properties.Properties): The properties associated with the unsubscribe request.
    """
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("Unsubscribe succeeded (if SUBACK is received in MQTTv3 it is considered a success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")

def on_message(client, userdata, message):
    """
    The default callback called when a message is received.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        message (paho.mqtt.client.MQTTMessage): The received message.
    """
    userdata.append(message.payload)
    print(f"Received message '{str(message.payload)}' on topic '{message.topic}' with QoS {message.qos}")

def on_publish(client, userdata, mid, reason_code, properties):
    """
    The callback called when a message has been published.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata (Any): The user data associated with the client.
        mid (int): The message ID of the published message.
        reason_code (paho.mqtt.packettypes.ReasonCode): The reason code for the publish (MQTTv5 only)
        properties (paho.mqtt.properties.Properties): The properties associated with the publish (MQTTv5 only)
    """
    #print(f"Published message with mid {mid}")    
    