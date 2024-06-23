# Game Parameters
NUM_TEAMS = 2
NUM_GROUPS = 2
GRID_ROWS = 20
GRID_COLS = 20
NUM_OBSTACLES = 40
TIMESTEP = 1000                                 # Time interval between each move in milliseconds

# Note, if the broker is running on WSL, you need to expose the broker's port to the host machine on another port
# For example, if the broker is listening on port 1883 in WSL, you can expose it to port 5000 on the host machine
# by running the following command in the PowerShell terminal:
# netsh advfirewall firewall add rule name="Allowing MQTT connections" dir=in action=allow protocol=TCP localport=5000
# netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=5000 connectaddress=localhost connectport=1883

# Network Parameters
BROKER_LOCAL_ADDRESS = "localhost"              # Client uses this if broker is running on the same machine
BROKER_PORT = 1883                              # Default MQTT port is 1883
BROKER_NETWORK_ADDRESS = "192.168.0.2"          # Client uses this if broker is running on another machine (same network)
BROKER_WSL_PORT = 5000                          # Client uses this if broker is running on WSL and exposed to the host machine
BROKER_SECURE_PORT = 8883                       # Default MQTT secure port is 8883 (over TCP)
BROKER_TLS_PORT = 443                           # Default MQTT secure port is 443 (over Websockets)
BROKER_SWSL_PORT = 5001                         # Secure Websockets port for WSL
BROKER_KEEP_ALIVE = 60                          # Keep the connection alive for 60 seconds
USERNAME = "user"                               # Username for broker authentication
PASSWORD = "password"                           # Password for broker authentication

# Connection Parameters
MSG_COUNT = 3