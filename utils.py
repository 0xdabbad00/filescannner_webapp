#!/usr/bin/python
# file: utils.py

import MySQLdb

def connectToDB():
	db = MySQLdb.connect(host="localhost",
	                     user="root",
	                      passwd="mypassword",
	                      db="scanner")
	cur = db.cursor()
	return cur, db