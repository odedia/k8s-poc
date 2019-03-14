#!/usr/bin/env python
import pika
import datetime
import requests
import json
import re
import requests_pkcs12

credentials = pika.PlainCredentials('user', '2wVEPkVLX9')
connection = pika.BlockingConnection(pika.ConnectionParameters('wise-frog-rabbitmq.default.svc.cluster.local',5672,'/',credentials))
channel = connection.channel()

channel.queue_declare(queue='sites')

def do_titles_match(data, r):
    print('do_titles_match()')
    try:
        expected_title = my_strip(data['Title'])
        actual_title = get_title(r.text)
        return [expected_title == actual_title, expected_title, actual_title]
    except Exception as e:
        print('Exception: {0}'.format(str(e)))
        return [False, 'Error', 'Error']

def get_title(body):
    print('get_title()')
    a = re.search('<(title|TITLE)>.*</(title|TITLE)>', body)
    title = a.group()[7:len(a.group())-8]
    if title is None:
        return ''
    else:
        title = my_strip(title)
        return title
    
def my_strip(text):
    print('my_strip()')
    try:
        return re.sub(' +', ' ', re.sub(r"[\n\t\s]", ' ', text)).strip()
    except Exception as e:
        print('Exception: {0}'.format(str(e)))
        return ''
    
def callback(ch, method, properties, body):
    data = json.loads(body)
    #print(" [x] Received %r" % data)
    
    timeout = False
    title_match = False
    is_title = False
    return_to_queue = True
    
    a = datetime.datetime.now()
    try:
        r = requests.get(data['Site'])
        # Need to bring the GalGadot.pfx file into the container
        #r = requests_pkcs12.get(data['Site'], pkcs12_filename='GalGadot.pfx', pkcs12_password='Tehila!@')
    except Exception as e:
        timeout = True
        log_message = "{0} Exception: {1} URL: {2}".format(str(datetime.datetime.now()), str(e), data['Site'])
        return_to_queue = False
    b = datetime.datetime.now()
    
    if not timeout:
        delta = b - a
        
        titles_match = do_titles_match(data, r)
        if not titles_match[0]:
            actual_title = titles_match[2]
            expected_title = titles_match[1]

        log_message = "{0} URL: {1} http status code: {2} took {3} seconds. Title match: {4}".format(str(datetime.datetime.now()),
                                                                              data['Site'],
                                                                              r.status_code,
                                                                              delta.total_seconds(),
                                                                              titles_match[0])
        if not titles_match[0]:
            log_message = "{0}, expected: {1}, found: {2}".format(log_message, expected_title, actual_title)
        if data['URLafterRedirect'] == r.url:
            log_message = "{0}, URL redirect as expected".format(log_message)
        else:
            log_message = "{0}, URL redirect mismatch. Expected: {1}, found: {2}".format(log_message, data['URLafterRedirect'], r.url)
    print(log_message)
    
    if return_to_queue:
        channel.basic_publish(exchange='', routing_key='sites', body=body)
        #print(" [x] Sent '%r'" % body)
    channel.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='sites',
                      no_ack=False)

print(' [*] Waiting for messages.')
try:
    channel.start_consuming()
except Exception as e:
    print('Problem somewhere in the code: ' + str(e))
