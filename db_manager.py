# -*- coding: utf-8 -*-

import psycopg2
import datetime
import sys
import time

conn = psycopg2.connect(
	dbname="djcn1g0nujems", 
	user="tfllcecncvrprm", 
	password="NbvO15Khr35UhZ7Vaowf_4afcz", 
	host="ec2-54-247-177-33.eu-west-1.compute.amazonaws.com")

cur = conn.cursor()

groupNames = []

def init():
	try:
		cur.execute("SELECT group_name FROM timetable;")
		result = cur.fetchall()

		for name in result:
			#print name[0].decode("utf-8")
			groupNames.append(name[0])

		#conn.commit()
	except psycopg2.Error as e:
		print e.pgerror
	return

def saveGroup(id, name):
	#if name in groupNames:
	try:
		cur.execute("UPDATE users SET group_name = %s WHERE id = %s; INSERT INTO users (id, group_name) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = %s)", (name, id, id, name, id))
		conn.commit()
		return True
	except psycopg2.Error as e:
		print e.pgerror
		return False
	return True

def getGroup(id):
	try:
		cur.execute("SELECT group_name FROM users WHERE id = %s LIMIT 1", (id,))
		result = cur.fetchone()
		return result[0]
	except psycopg2.Error as e:
		print e.pgerror
		return None
	return None

def getTimetable(name):
	#if name in groupNames:
	try:
		dt = datetime.datetime.now()
		if time.localtime().tm_isdst == 0:
			offset = time.timezone
		else:
			offset = time.altzone
		offset = offset / 60 / 60 * -1

		if offset == 0:
			dt = dt + datetime.timedelta(hours=5)

		cur.execute("SELECT today, tomorrow FROM timetable WHERE group_name = %s AND last_update = %s LIMIT 1", (name, dt.strftime("%Y.%m.%d")))
		result = cur.fetchone()
		
		print result, offset, time.tzname, time.gmtime(), datetime.datetime.now().strftime("%Y.%m.%d")
		return result
	except psycopg2.Error as e:
		print e.pgerror
		return []
	return []

def saveTimetable(name, today, tomorrow):
	try:
		#cur.execute("CREATE TABLE timetable (group_name varchar PRIMARY KEY, last_update date, today text[][], tomorrow text[][]) ENCODING='UTF8';")
		if name in groupNames:
			cur.execute("UPDATE timetable SET (last_update, today, tomorrow) = (%s, %s, %s) WHERE group_name = %s", (datetime.datetime.now(), today, tomorrow, name))
		else:
			cur.execute("INSERT INTO timetable (group_name, last_update, today, tomorrow) VALUES (%s, %s, %s, %s)", (name, datetime.datetime.now(), today, tomorrow))
		
		#cur.execute("SELECT * FROM timetable;")
		#result = cur.fetchall()
		#print result[1][0].decode("utf-8")

		conn.commit()
	except psycopg2.Error as e:
		print e.pgerror
	return

def close():
	cur.close()
	conn.close()
	return