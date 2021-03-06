import sqlite3
import ConfigParser
import datetime

import cv2

import os

"""
@author(s): Nathan Heidt

In charge of saving meteor events to either a remote server or on the local machine for debugging or future uploading.  
It will upload to local and/or remote databases depending on what is specified in the config.ini file.

TODO:
    - 

CHANGELOG:
    - 
"""


class EventLogger():
	def __init__(self, configPath='config.ini'):
		self.config = ConfigParser.ConfigParser()
		self.config.read(configPath)

		#get working variables from config file
		self.localDbName = self.config.get('Database', 'Local', 0)
		self.localDbTableName = self.config.get('Database', 'LocalTable', 0)
		self.remoteDbName = self.config.get('Database', 'Remote', 0)
		self.localImageLocation = self.config.get('Database', 'LocalImages', 0)

		self.useLocal = bool(self.config.get('Database', 'UseLocal', 0))
		self.useRemote = bool(self.config.get('Database', 'UseRemote', 0))

		self.conn = sqlite3.connect(self.localDbName)
		#connect to db and create tables if they don't exist
		self.checkLocalDb()
		
	def __del__(self):
		self.conn.close()

	def addEvent(self, curimg, previmg):
		date = datetime.datetime.utcnow().isoformat()
		#get settings from file
		lat = self.config.get('Location', 'Latitude', 0)
		lon = self.config.get('Location', 'Longitude', 0)
		bear = self.config.get('Location', 'Bearing', 0)
		roll = self.config.get('Location', 'Roll', 0)
		pitch = self.config.get('Location', 'Pitch', 0)
		yaw = self.config.get('Location', 'Yaw', 0)

		intrin = self.config.get('Camera', 'IntrinsicMat', 0)
		dist = self.config.get('Camera', 'DistortionCoeff', 0)

		if self.useLocal:
			self.uploadToLocal(curimg, previmg, date, lat, lon, bear, roll, pitch, yaw, intrin, dist)
		if self.useRemote:
			pass


	def uploadToRemote(self, curimg, previmg, date, lat, lon, bear, r, p, y, intrin, dist):
		pass

	def uploadToLocal(self, curimg, previmg, date, lat, lon, bear, r, p, y, intrin, dist):
		#save the images locally, we don't want them in the database so they're easier to work with
		filenamecur = filenameprev = self.localImageLocation + date	
		filenamecur += '_current'
		filenameprev += '_prev'
		filenamecur += '.jpg'
		filenameprev += '.jpg'

		cv2.imwrite(filenamecur, curimg)
		cv2.imwrite(filenameprev, previmg)

		#we want to save the absolute path filename
		self.conn.execute("insert into %s (curimg, previmg, date, latitude, longitude, bearing, roll, pitch, yaw, IntrinsicMat, DistortionCoeff) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
										% (self.localDbTableName, os.path.abspath(filenamecur), os.path.abspath(filenameprev), date, lat, lon, bear, r, p, y, intrin, dist))
		self.conn.commit()


	def checkLocalDb(self):
		sql = 'create table if not exists ' + self.localDbTableName + ' (curimg, previmg, date, latitude REAL, longitude REAL, bearing REAL, roll REAL, pitch REAL, yaw REAL, IntrinsicMat, DistortionCoeff)'
		c = self.conn.cursor()
		c.execute(sql)
		self.conn.commit()

		


if __name__ == "__main__":
	print("starting in test mode")
	e = EventLogger()

