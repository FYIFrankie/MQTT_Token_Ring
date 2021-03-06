import paho.mqtt.client as mqtt
import time
import socket
import fcntl
import struct
import sys
import os
import socket
import random
import threading

broker = ''
u_neighbor = ''
participant = False
leader = None
UID = random.randrange(1, 9999)

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

IP = get_lan_ip()



def main():
	global u_neighbor
	global broker
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


	client = mqtt.Client()
	client.will_set(get_lan_ip(), "dead - " + u_neighbor)
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_disconnect = on_disconnect
	client.connect(broker, 1883, 60)

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	threading.Thread(target=elect_leader, args=(client,)).start()
	client.loop_forever()


def elect_leader(client):
	global participant
	global leader
	if leader == None:
		print("Starting elect leader")
		participant = True
		client.publish(IP, payload='election - ' + str(UID))



def on_connect(client, userdata, flags, rc):
	global u_neighbor
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe(u_neighbor)
	print("Connected to broker: " + broker +  "\nSubscribed to topic: " + u_neighbor)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global u_neighbor
	global UID
	global participant
	global leader
	if "dead - " in msg.payload:
		client.unsubscribe(u_neighbor)
		print("Unsubscripted from " + u_neighbor)
		u_neighbor = msg.payload[7:]
		client.subscribe(u_neighbor)
		print("Subscribed to " + u_neighbor)
	elif "election - " in msg.payload:
		msg_UID = msg.payload[11:]
		if int(msg_UID) > UID:
			participant = True
			client.publish(IP, msg.payload)
		elif int(msg_UID) < UID:
			participant = True
			client.publish(IP, "election - " + str(UID))
		elif int(msg_UID) == UID:
			leader = get_lan_ip()
			client.publish(IP, "leader - " + str(leader))
			participant = False
	elif "leader - " in msg.payload:
			msg_leader = msg.payload[9:]
			print("Leader is " + msg_leader)
			if msg_leader != leader:
				leader = msg_leader
				participant = False
				client.publish(IP, msg.payload)
	else:
		print(msg.topic+" "+str(msg.payload))


def on_disconnect(client, userdata, rc):
	global u_neighbor
	print("Disconnected in a normal way")
	#client.publish(get_lan_ip(), "dead - " + u_neighbor)



if __name__ == '__main__':
	main()