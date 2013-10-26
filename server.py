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

from lockedlist import lockedlist
from debug import debug
from packet import packet
from buf import buf, EndOfBufError
from clientlist import clientlist
import tools

import time

class server:
	DBGTAG = "server"
	DBGTAG_READ = DBGTAG+"/read"
	DBGTAG_READINFO = DBGTAG+"/readinfo"
	DBGTAG_READFAIL = DBGTAG+"/readfail"
	DBGTAG_BUFDUMP = DBGTAG+"/bufdump"
	DBGTAG_CLIENTCNSDUMP = DBGTAG+"/clientcnsdump"
	DBGTAG_CLIENTDUMP = DBGTAG+"/clientdump"
	
	@staticmethod
	def getnumclients(srv):
		return srv.numclients
	
	@staticmethod
	def getnumclients_reverse(srv):
		return server.getnumclients(srv) * -1

	def __init__(self, host = None, port = None):
		self.selfreg = False # whether this server has registered to gamemod itself (and not arrived via sauerbraten.org)
		self.additional = False # whether this server has been fetched from the additional servers file
		self.suggested = False # whether this server has been suggested to gamemod (and not arrived via sauerbraten.org)
		
		self.quicktest = False
	
		self.host = host
		self.port = port
		self.regcallbacks = lockedlist()
		self.lastping = None
		self.pings = 0
		self.lastreply = None
		self.nextping = None
		self.firstping = None
		self.persistent = False
		self.fromfile = None
		
		self.lastextinforeply = None
		self.usealtextinfo = False
		
		self.clients = clientlist()
		
		self.numclients = -1
		self.version = -1
		self.gamemode = -1
		self.remaining = -1 # in seconds
		self.maxclients = -1
		self.mastermode = -1
		self.map = ""
		self.desc = ""
		
	def getremaining(self):	
		return self.remaining - (time.time() - self.lastreply)
	
	def addregcallback(self, func, args):
		self.regcallbacks.append((func, args))
	
	def callregcallbacks(self, succ):
		for (func, args) in self.regcallbacks.iterator():
			func(succ, *args)
		self.regcallbacks.clear()
	
	def succreg(self):
		self.callregcallbacks(True)
	
	def failreg(self):
		self.callregcallbacks(False)
	
	def onremove(self):
		self.failreg()
		
	def onregister(self):
		self.succreg()
	
	def readextinfo(self, buf):
		try:
			ack_ = buf.getint()
			if ack_ != packet.EXT_ACK: return False, "EXT_ACK (%d) expected, got %d instead" % (packet.EXT_ACK, ack_)
			version_ = buf.getint()
			if version_ != packet.EXT_VERSION: return False, "received unknown extinfo version %d" % version_
			error_ = buf.getint()
			if error_ != packet.EXT_NO_ERROR: return False, "extinfo request contains errors, expected EXT_NO_ERROR (%d), got %d instead" % (packet.EXT_NO_ERROR, error_)
		
			content_ = buf.getint()
			if content_ == packet.EXT_PLAYERSTATS_RESP_IDS:
				e = debug.tagenabled(server.DBGTAG_CLIENTCNSDUMP)
				if e:
					s = ""
					n = 0
				while buf.available():
					cn = buf.getint()
					self.clients.keep(cn) # keep this player
					if e:
						s += " " + str(cn)
						n += 1
				self.clients.keep() # remove players not called keep() on
				if e:
					debug.msg(server.DBGTAG_CLIENTCNSDUMP, "%s:%d: received %d cns:%s" % (self.host, self.port, n, s))
				
			elif content_ == packet.EXT_PLAYERSTATS_RESP_STATS:
				cn = buf.getint()
				ping = buf.getint()
				name = buf.getstring()
				team = buf.getstring()
				frags = buf.getint()
				flags = buf.getint()
				deaths = buf.getint()
				teamkills = buf.getint()
				damage = buf.getint()
				health = buf.getint()
				armour = buf.getint()
				gunselect = buf.getint()
				priv = buf.getint()
				state = buf.getint()
				ip = (buf.read(), buf.read(), buf.read())
				
				c = self.clients.get(cn)
				c.name = name
				c.team = team
				c.frags = frags
				c.flags = flags
				c.priv = priv
				c.state = state
				c.ip = ip
				
				if debug.tagenabled(server.DBGTAG_CLIENTDUMP):
					debug.msg(server.DBGTAG_CLIENTDUMP, "%s:%d: received client: cn=%d, name=\"%s\", team=\"%s\", frags=%d, flags=%d, priv=%d, ip=%d.%d.%d.x" % ((self.host, self.port, cn, name, team, frags, flags, priv)+ip))
			else:
				return False, "invalid content type, expected EXT_PLAYERSTATS_RESP_IDS (%d) or EXT_PLAYERSTATS_RESP_STATS (%d), got %d instead" % (packet.EXT_PLAYERSTATS_RESP_IDS, packet.EXT_PLAYERSTATS_RESP_STATS, content_)
				
		except EndOfBufError:
			return False, "end of buf unexpectedly reached"
		
		return True, ""
		
	def readinfo(self, buf):
		try:
			numclients_ = buf.getint()
			attrs_ = buf.getint()
			if attrs_ != 5: return False, "attrs is not 5"
			version_ = buf.getint()
			gamemode_ = buf.getint()
			remaining_ = buf.getint() # TODO: switch protocol versions (in sooner versions, remaining_ is in minutes)
			maxclients_ = buf.getint()
			mastermode_ = buf.getint()
			map_ = buf.getstring()
			desc_ = buf.getstring()
		except EndOfBufError:
			return False, "end of buf unexpectedly reached"
		
		debug.msg(server.DBGTAG_READINFO, "%s:%d: numclients=%d, attrs=%d, version=%d, gamemode=%d, remaining=%d, maxclients=%d, mastermode=%d, map=\"%s\", desc=\"%s\""
			% (self.host, self.port, numclients_, attrs_, version_, gamemode_, remaining_, maxclients_, mastermode_, map_, desc_))
			
		self.numclients = numclients_
		self.version = version_
		self.gamemode = gamemode_
		self.remaining = remaining_
		self.maxclients = maxclients_
		self.mastermode = mastermode_
		self.map = map_
		self.desc = tools.safe(desc_)
		
		return True, ""
				
	def read(self, buf, t):
		debug.msg(server.DBGTAG_READ, "%s:%d: reading %d bytes" % (self.host, self.port, buf.len()))
		if debug.tagenabled(server.DBGTAG_BUFDUMP):
			pos = buf.pos()
			s = ""
			while buf.available():
				try: s += " " + str(buf.getint())
				except EndOfBufError: break
			debug.msg(server.DBGTAG_BUFDUMP, "%s:%d: buf:%s" % (self.host, self.port, s))
			buf.seek(pos)

		req = buf.read()
		if (req == ord(packet.ALTEXTINFO_BYTE)) or (not req):
			# (standard/alternative) extinfo
			buf.skip(len(packet.ALTEXTINFO_DATA if (req == packet.ALTEXTINFO_BYTE) else packet.EXTINFO_DATA)-1)
			succ, msg = self.readextinfo(buf)
			if succ:
				self.lastextinforeply = t
				self.usealtextinfo = (req == packet.ALTEXTINFO_BYTE)
		else:
			succ, msg = self.readinfo(buf)
		if not succ:
			debug.msg(server.DBGTAG_READFAIL, "%s:%d: reading %d bytes of %sinfo failed: %s" % (self.host, self.port, buf.len(), "" if req else "ext", msg))
			
			
