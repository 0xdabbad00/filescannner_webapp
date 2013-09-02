#!/usr/bin/python
# file: yarascanner.py

import utils
import yara
import sys
from os import path
import pika
import md5

def scanFile(file_id):
    print "Scanning file %d" % file_id
    filename = '%s' % file_id
    filepath = path.join('uploads', filename)
    matches = rules.match(filepath)
    print matches

    for match in matches:
        stmt = "SELECT id FROM rules WHERE name = %(name)s AND enabled=1"
        cur.execute(stmt, {'name': match})
        rule_id = cur.fetchone()[0]
        
        stmt = "INSERT INTO matches (file_id, rule_id) VALUES (%(file_id)s, %(rule_id)s)"
        cur.execute(stmt, {'file_id': file_id, 'rule_id': rule_id})
        db.commit()

    # Get MD5 hash of file
    m = md5.new()
    with open(filepath, 'rb') as f:
        filedata = f.read()
    m.update(filedata)
    filehash = m.hexdigest()

    # Add the hash to the DB
    stmt = "UPDATE files SET md5 = %(md5)s WHERE id = %(id)s"
    cur.execute(stmt, {'md5': filehash, 'id': file_id})
    db.commit()



# Read rules from database
cur, db = utils.connectToDB()

stmt = "SELECT text FROM rules_text rt JOIN rules r ON rt.id = r.id WHERE r.enabled=1"
cur.execute(stmt)
storedRules = cur.fetchall()

# Join them
rulesText = ""
for rule in storedRules:
    rulesText += rule[0] + '\n'

# Load them into yara
rules = yara.compile(source=rulesText)


if len(sys.argv) > 1:
    scanFile(int(sys.argv[1]))

# RabbitMQ callback
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    scanFile(int(body))
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Consume messages from work queue
connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()
channel.queue_declare(queue='uploaded_files')
channel.basic_consume(callback,
                      queue='uploaded_files')

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()