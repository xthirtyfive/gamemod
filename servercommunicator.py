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

import threading
import time
import socket
from collections import deque

from debug import debug
from packet import packet
from buf import buf
import config

# ping servers and kick them out if they time out / add pending servers as registered if they reply in time
# handle replies from servers
class servercommunicator:
	LOOP_INTERVAL = 0.05
	
	EXTINFO_TIMEOUT = 30
	
	DBGTAG = "servercommunicator"
	DBGTAG_KICK = DBGTAG+"/kick"
	DBGTAG_KICKSERVER = DBGTAG+"/kickserver"
	DBGTAG_MOVESERVER = DBGTAG+"/moveserver"
	DBGTAG_RECV = DBGTAG+"/recv"
	DBGTAG_PING = DBGTAG+"/ping"
	DBGTAG_SENT = DBGTAG+"/sent"
	DBGTAG_UNKNOWNSERVER = DBGTAG+"/unknownserver"
	DBGTAG_SUCCREG = DBGTAG+"/succreg"

	def __init__(self, registeredservers, pendingservers):
		self.registeredservers_key = "registered servers"
		self.pendingservers_key = "pending servers"
		self.lists = {
			self.registeredservers_key: registeredservers,
			self.pendingservers_key: pendingservers
		}
		
		self.t = 0
		
		self.packetqueue = deque()
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setblocking(0)
		
		self.thread = threading.Thread(target=self.run)
		self.thread.daemon = True
		self.thread.start()
		
	def sendqueue(self):
		before = len(self.packetqueue)
		if before:
			while len(self.packetqueue):
				p = self.packetqueue.popleft()
				try:
					self.socket.sendto(p.data, p.addr)
				except:
					self.packetqueue.appendleft(p)
					break
				#print("sending packet to %s:%d" % (p.addr[0], p.addr[1]))
				#self.socket.sendto(p.data, 0, p.addr)
			now = len(self.packetqueue)
			if before != now:
				debug.msg(servercommunicator.DBGTAG_SENT, "sent %d of %d packets (%d packets left)" % (before-now, before, now))
	
	def ping(self, server, relposinlist=0.0):
		destport = server.port+1
		# server must already have been pinged and must have sent a reply which is less time ago than EXTINFO_TIMEOUT
		extinfotimeout = (server.lastping and server.lastreply and ((self.t-server.lastreply) < servercommunicator.EXTINFO_TIMEOUT) and ((self.t-server.lastping) < servercommunicator.EXTINFO_TIMEOUT) and ((not server.lastextinforeply) or ((self.t-server.lastextinforeply) > servercommunicator.EXTINFO_TIMEOUT)))
		
		#TODO
		if server.lastping and server.lastreply:
			print(	server.lastping,
				server.lastreply,
				(self.t-server.lastreply) < servercommunicator.EXTINFO_TIMEOUT,
				(self.t-server.lastping) < servercommunicator.EXTINFO_TIMEOUT,
				((not server.lastextinforeply) or ((self.t-server.lastextinforeply) > servercommunicator.EXTINFO_TIMEOUT))
			)
		else:
			print(server.lastping, server.lastreply)
		
		tryaltextinfo = (not extinfotimeout) if server.usealtextinfo else extinfotimeout
		debug.msg(servercommunicator.DBGTAG_PING, "pinging server at %s:%d%s (sending packets to port %d)" % (server.host, server.port, ((", %sreached extinfo timeout, using %s extinfo request" % ("" if extinfotimeout else "not ", "alternative" if tryaltextinfo else "standard")) if (extinfotimeout or server.usealtextinfo or tryaltextinfo) else ""), destport))
		if server.lastreply != None and server.lastping != None and server.lastreply > server.lastping: # this is the first ping after a reply has been received
			server.pings = 1
		else:
			server.pings += 1
		if not server.firstping: server.firstping = self.t
		server.lastping = self.t
		server.nextping = server.lastping + (config.PING_INTERVAL * (1 + (0 if server.quicktest else (relposinlist * config.PING_SPREADRATIO))))
		self.packetqueue.append(packet.pingpacket((server.host, destport)))
		if tryaltextinfo:
			# reached standard-extinfo timeout, try with alternative extinfo request
			self.packetqueue.append(packet.altextinfopacket((server.host, destport)))
		else:
			# standard-extinfo timeout has not been reached, proceed with standard extinfo request
			self.packetqueue.append(packet.extinfopacket((server.host, destport)))
		
	def kick(self, clist, name, server):
		debug.msg(servercommunicator.DBGTAG_MOVESERVER if server.persistent else servercommunicator.DBGTAG_KICKSERVER, "%s server at %s:%d from %s list%s (first ping: %s, last ping: %s, last reply: %s)" % ("moving persistent" if server.persistent else "kicking out", server.host, server.port, name, (" to %s list" % self.pendingservers_key) if server.persistent else "", ("never" if server.firstping == None else ("%f seconds ago" % (self.t-server.firstping))), ("never" if server.lastping == None else ("%f seconds ago" % (self.t-server.lastping))), ("never" if server.lastreply == None else ("%f seconds ago" % (self.t-server.lastreply)))))
		clist.remove(server)
		if server.persistent:
			self.lists[self.pendingservers_key].append_once(server)
		else:
			server.onremove()
		
	def register(self, server, rlist, plist):
		plist.removeall(server)
		rlist.append_once(server)
		debug.msg(servercommunicator.DBGTAG_SUCCREG, "registration of server %s:%d successful" % (server.host, server.port))
		server.quicktest = False
		server.onregister()
		
	def pingservers(self):
		kicklist = []
		for name in self.lists:
			clist = self.lists[name]
			total = float(clist.len())
			n = 0.0
			for server in clist.releasingiterator():
				if ((not server.persistent) or name != self.pendingservers_key) and server.lastping != None and server.nextping != None and server.nextping < self.t and (server.lastreply == None or server.lastreply < server.lastping) and server.pings >= (1 if server.quicktest else config.PINGS_GIVEUP):
					# server is either not persistent or is not in pending servers list (it will be added there) has been pinged once or more, time is reached for a new ping, but the number of pings before giving up is exceeded. kick server.
					kicklist.append(server)
				elif server.nextping == None or server.nextping < self.t:
					# last ping has been too long ago, or server was never pinged. ping it.
					self.ping(server, n/total)
				n += 1
			if len(kicklist) > 0:
				debug.msg(servercommunicator.DBGTAG_KICK, "kicking out %d servers from %s list" % (len(kicklist), name))
				for server in kicklist:
					self.kick(clist, name, server)
				del kicklist[:]
	
	def processdata(self, p):
		debug.msg(servercommunicator.DBGTAG_RECV, "received %d bytes from %s:%d" % ((len(p.data),)+p.addr))
		host = p.addr[0]
		servport = p.addr[1] - 1
		plist = self.lists[self.pendingservers_key]
		s = plist.find(host, servport)
		if s:
			# server from pending servers list has replied, move it to registered servers list
			rlist = self.lists[self.registeredservers_key]
			self.register(s, rlist, plist)
		else:
			# sender is not in pending servers list, look through other lists
			for name in self.lists:
				if name == self.pendingservers_key: continue
				clist = self.lists[name]
				s = clist.find(host, servport)
				if s: break
			if not s: #if no server was found in any list, return.
				debug.msg(servercommunicator.DBGTAG_UNKNOWNSERVER, "received %d bytes from an unknown server at %s:%d (packet sent from port %d)" % (len(p.data), host, servport, p.addr[1]))
				return
				# TODO maybe add the server directly, even though it did not announce itself via regserv command?
		s.lastreply = self.t
		s.read(buf(p.data), self.t) # hand over current time (self.t) so server can set s.lastextinforeply if this is extinfo
	
	def receive(self):
		while True:
			try:
				(data, addr) = self.socket.recvfrom(4096)
			except:
				break
			try:
				self.processdata(packet(data, addr))
			except:
				debug.exc(self)
	
	def run(self):	
		while True:
			self.t = time.time()
			try:
				self.pingservers()
				self.sendqueue()
				self.receive()
			except:
				debug.exc(self)
			now = time.time()
			time.sleep(max(0, servercommunicator.LOOP_INTERVAL - (now-self.t)))
			
			
