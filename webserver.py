#!/usr/bin/python
# file: webserver.py
 
import tornado.ioloop
import tornado.web
import tornado.escape

import utils
import pika
from datetime import datetime 

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.htm")


class GetFilesHandler(tornado.web.RequestHandler):
    def get(self):
        stmt = "SELECT id, submission_date, filename, size, md5 from files ORDER BY id DESC LIMIT 10"
        cur.execute(stmt)
        files = cur.fetchall()
        output = []
        for f in files:
            output.append([
                f[0],
                f[1].strftime('%Y-%m-%d %H:%M:%S'),
                f[2],
                f[3],
                f[4]])
        self.write(tornado.escape.json_encode(output))
        self.finish()


class GetMatchesHandler(tornado.web.RequestHandler):
    def get(self, file_id):
        stmt = "SELECT rule_id, description from matches m join rules r on m.rule_id = r.id where m.file_id = %(file_id)s"
        cur.execute(stmt, {'file_id': file_id})
        matches = cur.fetchall()
        output = []
        for m in matches:
            print m
            output.append({
                'rule_id': m[0],
                'description': m[1]
                })
        self.write(tornado.escape.json_encode(output))
        self.finish()


class GetRuleHandler(tornado.web.RequestHandler):
    def get(self, rule_id):
        stmt = "SELECT text from rules_text WHERE id = %(id)s"
        cur.execute(stmt, {'id': rule_id})
        rule = cur.fetchone()[0]
        self.write(rule)
        self.set_header('Content-Type', 'text/plain')
        self.finish()


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file_name = self.request.files['file'][0].filename
        file_contents = self.request.files['file'][0].body
        file_size = len(file_contents)

        stmt = "INSERT INTO files (filename, size) VALUES (%(filename)s, %(filesize)s)"
        cur.execute(stmt, {'filename': file_name, 'filesize': file_size})
        file_id = cur.lastrowid
        db.commit()

        with open("uploads/%s" % file_id, "wb") as f:
            f.write(file_contents)
        self.finish()

        # Queue work message
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                       'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='uploaded_files')
        channel.basic_publish(exchange='',
                      routing_key='uploaded_files',
                      body='%s' % file_id)
        connection.close()


cur, db = utils.connectToDB()
 
application = tornado.web.Application([
    (r"/file-upload", UploadHandler),
    (r"/getFiles", GetFilesHandler),
    (r"/getMatches/([0-9]+)", GetMatchesHandler),
    (r"/getRule/([0-9]+)", GetRuleHandler),
    (r"/", MainHandler),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
])
 
if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
