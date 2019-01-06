#!/usr/bin/env python
import paho.mqtt.client as mqtt

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.payload))

# If you want to use a specific client id, use
# mqttc = mqtt.Client("mqtt-snooper")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect("10.1.1.2", 1883, 60)
mqttc.subscribe("#", 0)
mqttc.loop_forever()
