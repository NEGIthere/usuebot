# -*- coding: utf-8 -*-

import requests
import sys
import re
import urllib
import datetime
import db_manager
import time

daysOfWeek =  { "Monday":u"Понедельник", 
				"Tuesday":u"Вторник", 
				"Wednesday":u"Среда", 
				"Thursday":u"Четверг", 
				"Friday":u"Пятница", 
				"Saturday":u"Суббота", 
				"Sunday":u"Воскресенье" }

now = datetime.datetime.now()

def updateTimeTable(groupName):
	param = urllib.quote_plus(groupName.encode('cp1251'))

	try:
		r = requests.get("http://webrasp.usue.ru/rsp/RaspMain?DATN=" + 
						(now).strftime("%d.%m.%Y") + 
						"&DATK=" + (now + datetime.timedelta(days=1)).strftime("%d.%m.%Y") + 
						"&RASP=1&NAMGRP=" + param)
		r.encoding = "cp1251"

		data = r.text.decode("utf-8", "replace")

		#f = open('data.txt', mode='w')
		#f.write(data)
		#f.close()
	except requests.ChunkedEncodingError as e:
		return False

	today = [[u"null",u"null",u"null",]] * 8
	tomorrow = [[u"null",u"null",u"null",]] * 8

	if data.find("getDataTable()\n {\n }") > 0:
		print u"Нет расписания для", groupName.decode("utf-8")
		db_manager.saveGroup(groupName, today, tomorrow)
		return True

	i0 = data.find("ion getDataTable()\n {", 30000) + 22
	data = data[i0:]
	i1 = data.find("}") - 2
	data = data[:i1]

	i, j = 0, 0
	newi = 0
	first = True
	firstDate = True

	arr = data.split("\n")

	ind = 0
	
	parsingTomorrow = False

	r.close()

	# Sorting shitty constructed array
	while ind < len(arr):
		line = arr[ind].strip()
		arr[ind] = line

		if line.startswith("rows"):
			arr[ind], arr[ind+1] = arr[ind+1].strip(), arr[ind]
			ind = ind + 2
			continue
		ind = ind + 1

	# Parsing data
	for index, line in enumerate(arr):
		if line.startswith("rows"):
			m = re.search("Data='(.+)'", line)
			dstr = m.group(1)
			
			date = datetime.datetime.strptime(dstr, '%d.%m.%Y')

			

			if firstDate:
				firstDate = False
			else:
				if dateNew != date:
					parsingTomorrow = True

			dateNew = date

			print daysOfWeek[date.strftime("%A")] + ": " + subj + ", " + master  + ", " + aud

			ind = int((i - 1) % 9.0 - 1)
			print ind
			if parsingTomorrow:
				tomorrow[ind] = [subj, master, aud]
			else:
				today[ind] = [subj, master, aud]

			continue
		else:
			m = re.search('rows\[(\d+)\]', line)
			i = int(m.group(1))
			m = re.search('cells\[(\d+)\]', line)
			newj = int(m.group(1))
			j = newj

			if j == 2:
				m = re.search("predm\">(.+)<", line)
				subj = m.group(1)
				subj = re.sub(r' +', ' ', subj)
			elif j == 3:
				m = re.search("prep\">(.+)<", line)
				master = m.group(1)
			elif j == 4:
				m = re.search("aud (\w+)\">(.+)<", line)
				aud = m.group(2)
		print line
	if not parsingTomorrow and date.day != now.day:
		today, tomorrow = tomorrow, today
	db_manager.saveGroup(groupName, today, tomorrow)
	print "Saved", groupName.decode("utf-8")
	return True

def updateAllTimeTable():
	flag = True

	if len(sys.argv) > 1:	
		group = (sys.argv[1].decode(sys.getfilesystemencoding()))
		updateTimeTable(group)
	else:
		with open('groups_active.txt', mode='r') as fileGroups:
			lines = fileGroups.readlines()
			for line in lines:
				line = line.strip()
				if flag == False:
					if line == u"БД-13-2":
						flag = True
					continue
				ready = False
				while not ready:
					ready = updateTimeTable(line)

				time.sleep(10)
			fileGroups.close()

	db_manager.close()

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')
	db_manager.init()
	updateAllTimeTable();