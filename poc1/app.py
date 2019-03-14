#!/usr/bin/env python
import pika
import json
import requests
import os
from flask import Flask
app = Flask(__name__)

credentials = pika.PlainCredentials('user', '2wVEPkVLX9')
connection = pika.BlockingConnection(pika.ConnectionParameters('wise-frog-rabbitmq.default.svc.cluster.local',5672,'/',credentials))
channel = connection.channel()

channel.queue_declare(queue='sites')

data = json.loads(requests.get('https://raw.githubusercontent.com/abarlev/poc1/master/SiteList.json').text)

for row in data:
    serialized = json.dumps(row)
    channel.basic_publish(exchange='', routing_key='sites', body=serialized)
    print("published row = {0}".format(serialized))

print(" [x] Queue initialized")
connection.close()

@app.route('/push')
def hello():
       credentials = pika.PlainCredentials('user', '2wVEPkVLX9')
       connection = pika.BlockingConnection(pika.ConnectionParameters('wise-frog-rabbitmq.default.svc.cluster.local',5672,'/',credentials))
       
       channel = connection.channel()

       channel.queue_declare(queue='sites')

       data = json.loads(requests.get('https://raw.githubusercontent.com/abarlev/poc1/master/SiteList.json').text)

       for row in data:
           serialized = json.dumps(row)
           channel.basic_publish(exchange='', routing_key='sites', body=serialized)
           print("published row = {0}".format(serialized))

       print(" [x] Queue initialized")
       connection.close()
       return 'Hello World from Flask!'

port = os.getenv('PORT', '8080')
if __name__ == "__main__":
       app.run(host='0.0.0.0', port=int(port))

