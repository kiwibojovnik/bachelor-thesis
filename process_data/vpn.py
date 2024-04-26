from openvpn_api import Client

# Define the path to your OpenVPN client configuration file
config_file = 'process_data/vpn.ovpn'

# Initialize a Client object with the path to your OpenVPN client configuration file
client = Client(config_file)

# Connect to the OpenVPN server
client.connect()

# Check if the connection was successful
if client.is_connected():
    print("Connected to VPN!")
else:
    print("Failed to connect to VPN.")

# Disconnect from the OpenVPN server
# client.disconnect()
