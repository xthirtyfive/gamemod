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

import socket
import types

class additionalservers:
	DBGTAG = "additionalservers"
	DBGTAG_UPDATING = DBGTAG+"/updating"
	DBGTAG_ADD = DBGTAG+"/add"
	DBGTAG_REMOVED = DBGTAG+"/removed"
	DBGTAG_UPDATED = DBGTAG+"/updated"
	DBGTAG_INVALID = DBGTAG+"/invalid"
	DBGTAG_SKIP = DBGTAG+"/skip"
	
	COMMENT_STR = "//"

	def __init__(self, registeredservers, pendingservers, bannedservers):
		self.registeredservers = registeredservers
		self.pendingservers = pendingservers
		self.bannedservers = bannedservers
		
		self.serverspath = "servers.cfg"
		self.bannedpath = "banned.cfg"
		
		self.servers_list = []
		self.banned_list = []
	
	def checklists(self):
		# check if any of the contained servers is banned
		self.registeredservers.check()
		self.pendingservers.check()
		self.bannedservers.check()
	
	def load(self):
		self.update(False)
	
	def update(self, catch=True):
		self.updateservers(catch, False)
		self.updatebanned(catch, False)
	
	def updateservers(self, catch=True, checklists=True):
		succ, msg, self.servers_list = self.fetch(catch, self.serverspath, ((self.pendingservers, "pending"), (self.registeredservers, "registered")), self.servers_list, add_once = True)
		if checklists: self.checklists()
		return succ, msg
	
	def updatebanned(self, catch=True, checklists=True):
		succ, msg, self.banned_list = self.fetch(catch, self.bannedpath, ((self.bannedservers, "banned"),), self.banned_list, needport=False)
		if checklists: self.checklists()
		return succ, msg
	
	def fetch(self, catch, path, synclists, oldlist, needport=True, add_once=False):
		# sync synclist (read it from file, add unexisting servers, remove servers no more in file (compare read items with oldlist)) and return a list of fetched items (which will be used as oldlist next time
		
		debug.msg(additionalservers.DBGTAG_UPDATING, "updating %d server list%s with servers from file %s" % (len(synclists), "s" if len(synclists) > 1 else "", path))
		
		try:
			f = open(path, "r")
			
			newlist = []
			addlist = []
			
			n = 0 # line number
			errors = 0
			for line_ in f:
				n += 1
				if line_[-1] == "\n": line = line_[:-1]
				else: line = line_
				if len(line) <= 0 or line.startswith(additionalservers.COMMENT_STR): continue
				p = line.split(" ")
				if len(p) < 2 and needport:
					debug.msg(additionalservers.DBGTAG_INVALID, "can't fetch server from line %d in file %s" % (n, path))
					errors += 1
				else:
					whost = p[0]
					if len(p) >= 2:
						try:
							port = int(p[1])
						except:
							debug.msg(additionalservers.DBGTAG_INVALID, "can't fetch port for server at %s from line %d in file %s" % (whost, n, path))
							errors += 1
							continue
					else:
						port = "*"
					try:
						host = socket.gethostbyname(whost)
					except:
						debug.msg(additionalservers.DBGTAG_INVALID, "can't resolve host %s for server at %s:%s from line %d in file %s" % (whost, whost, str(port), n, path))
						errors += 1
						continue
						
					item = (host, port)
					newlist.append(item)
					addlist.append(item)

					
			f.close()
			
			dellist = []
			
			for old in oldlist:
				if addlist.count(old): addlist.remove(old) # was added already
				else: dellist.append(old) # was removed from file
			
			for (synclist, listname) in synclists:
				for (host, port) in dellist:
					s = synclist.find(host, port)
					if s and s.fromfile == path:
						synclist.removeall(s)
						debug.msg(additionalservers.DBGTAG_REMOVED, "removed server at %s:%s from %s servers list" % (host, str(port), listname))
			
			for (host, port) in addlist:
				if add_once: # don't add this anywhere if it already exists in any of the supplied synclists
					skip = False
					for (list_, name) in synclists:
						if list_.find(host, port):
							skip = True
							break
					if skip:
						debug.msg(additionalservers.DBGTAG_SKIP, "skipping server %s:%s from file %s because it already exists in the supplied synclists" % (host, str(port), path))
						continue
				debug.msg(additionalservers.DBGTAG_ADD, "adding server at %s:%s to %s servers list" % (host, str(port), synclists[0][1]))
				synclists[0][0].add_from_file(host, (port if (type(port) == types.IntType) else None), file=path)
				
			debug.msg(additionalservers.DBGTAG_UPDATED, "updated %d server list%s with servers from file %s: %d items fetched from %d lines, %d errors, %d items added, %d items deleted" % (len(synclists), "s" if len(synclists) > 1 else "", path, len(newlist), n, errors, len(addlist), len(dellist)))
			
			return True, "%d items fetched from %d lines, %d errors (skipping lines with errors), %d items added, %d items deleted" % (len(newlist), n, errors, len(addlist), len(dellist)), newlist
			
		except:
			if catch:
				debug.exc(self)
				try: f.close()
				except: pass
			else:
				try: f.close()
				except: pass
				raise
		return False, "internal errors occurred", oldlist
		
