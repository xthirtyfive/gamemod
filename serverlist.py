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

from threading import Lock
from server import server
from lockedlist import lockedlist
from debug import debug

class serverlist:
	DBGTAG = "serverlist"
	DBGTAG_INVALIDPORT = DBGTAG+"/invalidport"
	DBGTAG_REFUSED = DBGTAG+"/refused"
	DBGTAG_DELBANNED = DBGTAG+"/delbanned"
	DBGTAG_DELBANNEDSERVERS = DBGTAG+"/delbannedservers"

	def __init__(self, banned=None):
		self.list = lockedlist()
		self.releasingiterator = self.list.releasingiterator
		self.banned = banned
		
	def _append(self, server):
		self.list.append(server)
	
	def _isbanned(self, s, port=None):
		if not self.banned: return False
		if port != None: # got ip & port as arguments
			return self.banned.find(s, port)
		else: # got server instance as arguments
			return self.banned.find(s.host, s.port)
		
	# ---- public ----
	
	def find(self, host, port):
		for s in self.list.iterator():
			if s.host == host and (s.port == port or s.port == None): return s
		return None
	
	def exists(self, server):
		return self.list.count(server)
	
	def len(self):
		return self.list.len()
	
	def sort(self):
		self.list.sort(server.getnumclients_reverse)
	
#	def releasingiterator(self):
#		-> set in constructor

	def remove(self, item):
		self.list.remove(item)
	
	def removeall(self, item):
		self.list.removeall(item)
	
	def findandremoveall(self, host, port):
		s = self.find(host, port)
		if s:
			self.removeall(s)
		return s
	
	def check(self):
		if not self.banned: return
		dellist = []
		for s in self.list.iterator():
			if self._isbanned(s):
				dellist.append(s)
		if len(dellist):
			debug.msg(serverlist.DBGTAG_DELBANNEDSERVERS, "removing %d banned servers" % len(dellist))
			for s in dellist:
				debug.msg(serverlist.DBGTAG_DELBANNED, "removing banned server at %s:%d" % (s.host, s.port))
				self.remove(s)
				s.onremove()
				
	
	# ---- non list-accessing functions ----
	
	def append_once(self, server):
		if not self.exists(server):
			if not self._isbanned(server):
				self._append(server)
			else:
				debug.msg(serverlist.DBGTAG_REFUSED, "refused a banned server at %s:%d" % (server.host, server.port))
	
	def add_once(self, host, port, selfreg=False, suggested=False, persistent=False, force=False, checkport=True, file=None, quicktest=False): # add server if it doesn't already exist, return (serverobject, existed)
		if (not force) and self._isbanned(host, port):
			debug.msg(serverlist.DBGTAG_REFUSED, "refused a banned server at %s:%d" % (host, port))
			return None, False
		else:
			if checkport and (port < 0 or port > 65534):
				debug.msg(serverlist.DBGTAG_INVALIDPORT, "trying to add a new server with an invalid port: %s:%d" % (host, port))
				return
			s = self.find(host, port)
			if s:
				existed = True
			else:
				s = server(host, port)
				self._append(s)
				existed = False
			if selfreg: s.selfreg = True # whether this server has registered itself to gamemod (and not arrived via sauerbraten.org)
			if (not existed) and suggested: s.suggested = True # whether this server has been suggested to gamemod and was unknown before (and not arrived via sauerbraten.org)
			if persistent: s.persistent = True # whether this server should never be kicked from the pending servers list
			if file: s.fromfile = file
			if (not existed) and quicktest: s.quicktest = True # whether this server should be tested for registration quickly (= kick it if it does not already reply within one request and config.PING_INTERVAL)
			return s, existed
	
	def add_from_master(self, host, port): # servers arriving from sauerbraten.org, this is called by masterclient
		self.add_once(host, port)
	
	def add_from_regserv(self, host, port): # servers arriving from registering themselves to gamemod explicitly, this is called by masterserver
		return self.add_once(host, port, selfreg=True)
	
	def add_from_suggest(self, host, port): # servers arriving from being suggested by somebody to gamemod explicitly, this is called by masterserver
		return self.add_once(host, port, suggested=True, quicktest=True)
		
	def add_from_file(self, host, port, file=None): # servers arriving from a local file, this is called by additionalservers. don't check for bans.
		self.add_once(host, port, persistent=True, force=True, checkport=False, file=file)
		
