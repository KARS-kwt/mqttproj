import paho.mqtt.client as mqtt
import ssl

version = '5' # or '3'
mytransport = 'websockets' # or 'tcp'

# Choose which protocol version and create a client object
if version == '5':
    client = mqtt.Client(client_id="myPy",
                         transport=mytransport,
                         protocol=mqtt.MQTTv5)
if version == '3':
    client = mqtt.Client(client_id="myPy",
                         transport=mytransport,
                         protocol=mqtt.MQTTv311,
                         clean_session=True)
    
# Client Authentification and TLS setup
client.username_pw_set("user", "password")
client.tls_set(certfile=None,
               keyfile=None,
               # If these arguments above are not None then they will
               # be used as client information for TLS based
               # authentication and authorization (depends on broker setup).
               cert_reqs=ssl.CERT_REQUIRED)
               # this makes it mandatory that the broker
               # has a valid certificate

#Define the callbacks
import mycallbacks
client.on_connect = mycallbacks.on_connect
client.on_message = mycallbacks.on_message
client.on_publish = mycallbacks.on_publish
client.on_subscribe = mycallbacks.on_subscribe

# Connect to the broker
broker = 'YOUR-BROKER-ADDRESS' # eg. choosen-name-xxxx.cedalo.cloud
myport = 443
if version == '5':
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes 
    properties=Properties(PacketTypes.CONNECT)
    properties.SessionExpiryInterval=30*60 # in seconds
    client.connect(broker,
                   port=myport,
                   clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                   properties=properties,
                   keepalive=60)

if version == '3':
    client.connect(broker,port=myport,keepalive=60)

client.loop_start()

# Subscribe to topic
mytopic = 'topic/important'
client.subscribe(mytopic,2)

# Publish to topic
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
properties=Properties(PacketTypes.PUBLISH)
properties.MessageExpiryInterval=30 # in seconds
client.publish(mytopic,'Cedalo Mosquitto is awesome',2,properties=properties)

# Unsubscribe and close connection
client.unsubscribe(mytopic)
client.disconnect()