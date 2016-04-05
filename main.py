import paho.mqtt.client as mqtt
import time
import socket
import fcntl
import struct
import sys


try:
	broker = sys.argv[1]
except IndexError as e:
	print("Argument 1 should be the broker")
	sys.exit(1)
try:
	u_neighbor = sys.argv[2]
except IndexError as e:
	print("Argument 2 should be the upstream neighbor")
	sys.exit(1)
try:
	d_neighbor = sys.argv[3]
except IndexError as e:
	print("Argument 3 should be the downstream neighbor")
	sys.exit(1)

def get_first3_octets():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	return s.getsockname()[0]


def on_connect(client, userdata, flags, rc):
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe(u_neighbor)
	print("Connected to broker: " + broker +  "\nSubscribed to topic: " + u_neighbor)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	if "dead" in msg.payload:
		client.unsubscribe(u_neighbor)
		print("Unsubscripted from " + u_neighbor)
		u_neighbor = msg.payload[7:]
		client.subscribe(u_neighbor)
		print("Subscribed to " + u_neighbor)
	else:
		print(msg.topic+" "+str(msg.payload))


def on_disconnect(client, userdata, rc):
	time.sleep(1)
	client.connect(broker, 1883, 60)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.will_set(d_neighbor, "dead - " + u_neighbor)

client.connect(broker, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()