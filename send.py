import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.

broker = '127.0.0.1'

client = mqtt.Client()
client.connect(broker, 1883, 60)
client.publish('this_is_a_test', payload="This is a test")