#!/usr/bin/env python
import pika
import json
import requests
import os
from flask import Flask

app = Flask(__name__)


if 'VCAP_SERVICES' in os.environ:
    services = json.loads(os.getenv('VCAP_SERVICES'))
    rabbit_env = services['p.rabbitmq'][0]['credentials']
else:
    rabbit_env = dict(hostname='localhost', port=5672, password='')


credentials = pika.PlainCredentials(rabbit_env['username'], 
                                    rabbit_env['password'])
connection = pika.BlockingConnection(pika.ConnectionParameters(
  rabbit_env['hostname'],
  5672,
  rabbit_env['vhost'],
  credentials))
channel = connection.channel()

channel.queue_declare(queue='sites')

data = json.loads(requests.get('https://raw.githubusercontent.com/odedia/poc1/master/SiteList.json').text)

for row in data:
    serialized = json.dumps(row)
    channel.basic_publish(exchange='', routing_key='sites', body=serialized)
    print("published row = {0}".format(serialized))

print(" [x] Queue initialized")
connection.close()

@app.route('/push')
def hello():
  if 'VCAP_SERVICES' in os.environ:
      services = json.loads(os.getenv('VCAP_SERVICES'))
      rabbit_env = services['p-rabbitmq'][0]['credentials']
  else:
      rabbit_env = dict(hostname='localhost', port=5672, password='')


  credentials = pika.PlainCredentials(rabbit_env['username'], 
                                      rabbit_env['password'])
  connection = pika.BlockingConnection(pika.ConnectionParameters(
    rabbit_env['hostname'],
    5672,
    rabbit_env['vhost'],
    credentials))
  channel = connection.channel()
   
  channel.queue_declare(queue='sites')

  data = json.loads(requests.get('https://raw.githubusercontent.com/odedia/poc1/master/SiteList.json').text)

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

