#    Copyright 2013 X35
#
#    This file is part of gamemod.
#
#    gamemod is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    gamemod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gamemod.  If not, see <http:#www.gnu.org/licenses/>.

from debug import debug
from lockedlist import lockedlist
import threading
import socket
import time
import config

# fetch gameservers from another masterserver
class masterclient:
	DBGTAG = "masterclient"
	DBGTAG_FETCHED = DBGTAG+"/fetched"
	DBGTAG_INVALID = DBGTAG+"/invalid"

	ADDSERVER_COMMAND = "addserver"

	def __init__(self, list_):
		self.interval = config.MASTER_FETCH_INTERVAL
		self.host = config.MASTER_ADDR
		self.port = config.MASTER_PORT
		
		self.list = list_
		self.thread = threading.Thread(target=self.run)
		self.thread.daemon = True
		self.thread.start()
	
	# ---
	
	def run(self):
		while True:
			try:
				self.updatefrommaster()
			except:
				debug.exc(self)
			time.sleep(self.interval)
	
	def connect(self):
		return socket.create_connection((self.host, self.port))
		
	def processline(self, line):
		if line[:len(masterclient.ADDSERVER_COMMAND)] != masterclient.ADDSERVER_COMMAND:
			debug.msg(masterclient.DBGTAG_INVALID, "received invalid line from master, does not start with \"%s\": %s" % (masterclient.ADDSERVER_COMMAND, line))
			return
		a = line[len(masterclient.ADDSERVER_COMMAND)+1:]
		p = a.split(" ")
		if len(p) < 2:
			debug.msg(masterclient.DBGTAG_INVALID, "received invalid line from master, does not contain 2 arguments: %s" % line)
			return
		host = p[0]
		port = int(p[1])
		self.list.add_from_master(host, port)
	
	def process(self, s):
		lines = s.split("\n")
		for line in lines:
			if len(line): self.processline(line)
	
	def fetch(self, sock):
		s = ""
		while True:
			s += sock.recv(4096)
			e = (s[-1] == "\x00")
			if (not s[-1] == "\n") and (not e): continue
			self.process(s[:-1] if e else s)
			if e: return # "\x00" = end
	
	def updatefrommaster(self):
		s = self.connect()
		s.send("list\n")
		self.fetch(s)
		s.close()
		debug.msg(masterclient.DBGTAG_FETCHED, "fetched %d servers from master" % self.list.len())


