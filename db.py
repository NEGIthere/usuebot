# -*- coding: utf-8 -*-

import psycopg2

conn = psycopg2.connect(
	dbname="djcn1g0nujems", 
	user="tfllcecncvrprm", 
	password="NbvO15Khr35UhZ7Vaowf_4afcz", 
	host="ec2-54-247-177-33.eu-west-1.compute.amazonaws.com")

cur = conn.cursor()

def savegroup(name, today, tomorrow):
	try:
		#cur.execute("CREATE TABLE timetable (group_name varchar PRIMARY KEY, last_update date, today text[][], tomorrow text[][]) ENCODING='UTF8';")
		#cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
		cur.execute("SELECT * FROM timetable;")
		result = cur.fetchone()
		print result[0].decode("utf-8")

		conn.commit()

		cur.close()
		conn.close()
	except psycopg2.Error as e:
		print e.pgerror
	return