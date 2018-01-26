#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# MQTT Consumer
# retrieve date from mqtt server, then send to the celery task
"""
import traceback
import paho.mqtt.client as mqtt
from bson.json_util import loads
from cfgparser import parser
from tasks import data_type, record_to_mongodb


# EMQTT Connector
client = mqtt.Client("5962eeea4acbdc394cdb05f5", clean_session=False)
client.username_pw_set(parser.euser, parser.epass)


# MQTT Setting
def on_connect(client, userdata, flags, rc):
    # '+': match one step，'#'：match all children stop
    print "Connected with result code " + str(rc)
    client.subscribe("/spider/message_cache", qos=2)


def on_message(client, userdata, msg):
    try:
        print msg.topic + " " + str(msg.payload)
        payload = loads(msg.payload)
        data = payload["body"]
        for item in data:
            chain = (data_type.s(item) | record_to_mongodb.s())
            chain.apply_async()
    except Exception as exc:
        traceback.print_exc()


def consumer():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(parser.ehost, port=int(parser.eport), keepalive=int(parser.keepalive))
    client.loop_forever()

if __name__ == "__main__":
    consumer()
