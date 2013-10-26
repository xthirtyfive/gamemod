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
from debug import debug

import socket

# let gameservers register at this & let gameclients fetch gameservers from this
class masterserver:
	class regservlock:
		def __init__(self):
			self.regserv_succ = None
			self.lock = Lock()
		def wait(self):
			self.lock.acquire()
			self.lock.acquire() # try to acquire the lock the 2nd time, this blocks until resume is called, then continue here
			return self.regserv_succ
		def resume(self, succ = None):
			self.regserv_succ = succ
			try:
				self.lock.release()
				self.lock.release() # 2nd release neccessary for re-use
			except:
				pass

	REGSERV_COMMAND = "regserv"
	SUGGEST_COMMAND = "suggest"
	SUCCREG_COMMAND = "succreg"
	FAILREG_COMMAND = "failreg"
	
	DBGTAG = "masterserver"
	DBGTAG_INVALID = DBGTAG+"/invalid"
	DBGTAG_REGSERV = DBGTAG+"/regserv"
	DBGTAG_SUGGEST = DBGTAG+"/suggest"
	DBGTAG_INVALIDPORT = DBGTAG+"/invalidport"

	def __init__(self, registeredservers, pendingservers):
		self.registeredservers = registeredservers
		self.pendingservers = pendingservers
	
	def resume_regserv(self, succ, lock): # called by the servercommunicator thread, makes regserv() continue
		lock.resume(succ)
	
	def regserv(self, ip, port): # returns (success, existed, banned)
		"""lock = masterserver.regservlock()
		s, existed = self.pendingservers.add_from_regserv(ip, port)
		if not s:
			return False, True
		if existed:
			return True, False
		else:
			s.addregcallback(self.resume_regserv, (lock,))
			return lock.wait(), False # wait for callback to resume this, then return success bool"""
		s = self.registeredservers.find(ip, port)
		if s:
			return True, True, False # server already registered
		s, existed = self.pendingservers.add_from_regserv(ip, port)
		if not s:
			return False, False, True # banned
		lock = masterserver.regservlock()
		s.addregcallback(self.resume_regserv, (lock,))
		return lock.wait(), False, False # trying to register - wait for callback to resume this, then return success bool
	
	def suggest(self, ip, port): # returns (success, existed, banned)
		s = self.registeredservers.find(ip, port)
		if s:
			return True, True, False # server already registered
		s, existed = self.pendingservers.add_from_suggest(ip, port)
		if not s:
			return False, False, True # banned
		lock = masterserver.regservlock()
		s.addregcallback(self.resume_regserv, (lock,))
		return lock.wait(), False, False # trying to register - wait for callback to resume this, then return success bool
			
	
	def onrequest(self, line, addr, build): # return reply, close
		if line.startswith(masterserver.REGSERV_COMMAND):
			port = False
			try:
				port = int(line[len(masterserver.REGSERV_COMMAND)+1:])
			except:
				debug.msg(masterserver.DBGTAG_INVALID, "could not get port from line received from %s:%d: %s" % (addr+(line,)))
				return None, False
			if port < 0 or port > 65534:
				debug.msg(masterserver.DBGTAG_INVALIDPORT, "server tried to register with invalid port: %d" % port)
				return ("%s wtf port? %d?" % (masterserver.FAILREG_COMMAND, port)), True
			debug.msg(masterserver.DBGTAG_REGSERV, "trying to register server at port %d (received from %s:%d)" % ((port,)+addr))
			succ, existed, banned = self.regserv(addr[0], port)
			debug.msg(masterserver.DBGTAG_REGSERV, "registration of %sserver at %s:%d (received from %s:%d) %s%s" % ((("existing " if existed else ""), addr[0], port)+addr+(("succeeded" if succ else "failed"), (", address is banned" if banned else ""))))
			if succ:
				return masterserver.SUCCREG_COMMAND, True
			else:
				if banned:
					return ("%s you are banned from this masterserver" % masterserver.FAILREG_COMMAND), True
				else:
					return (("%s no reply received after requesting from %s:%d") % (masterserver.FAILREG_COMMAND, addr[0], port+1)), True
					
		elif line.startswith(masterserver.SUGGEST_COMMAND):
			port = False
			try:
				addr_s = line[len(masterserver.REGSERV_COMMAND)+1:].split(" ")
				host_s = addr_s[0]
				port = int(addr_s[1])				
			except:
				debug.msg(masterserver.DBGTAG_INVALID, "could not get host and port from line received from %s:%d: %s" % (addr+(line,)))
				return ("%s could not parse command, use: %s host port" % (masterserver.FAILREG_COMMAND, masterserver.SUGGEST_COMMAND)), True
			if port < 0 or port > 65534:
				debug.msg(masterserver.DBGTAG_INVALIDPORT, "client tried to suggest a server with an invalid port: %d" % port)
				return ("%s wtf port? %d?" % (masterserver.FAILREG_COMMAND, port)), True
			try:
				host = socket.gethostbyname(host_s)
			except:
				debug.msg(masterserver.DBGTAG_INVALID, "could not get host and port from line received from %s:%d: %s" % (addr+(line,)))
				return ("%s could not resolve %s" % (masterserver.FAILREG_COMMAND, host_s)), True
			debug.msg(masterserver.DBGTAG_SUGGEST, "trying to register suggested server at %s:%d (%s) (received from %s:%d)" % ((host, port, host_s)+addr))
			succ, existed, banned = self.suggest(host, port)
			debug.msg(masterserver.DBGTAG_SUGGEST, "registration of %ssuggested server at %s:%d (received from %s:%d) %s%s" % ((("existing " if existed else ""), host, port)+addr+(("succeeded" if succ else "failed"), (", address is banned" if banned else ""))))
			if succ:
				return ("%s the server at %s:%d %s" % (masterserver.SUCCREG_COMMAND, host, port, ("has already been registered" if existed else "is now registered"))), True
			else:
				if banned:
					return ("%s %s:%d is banned from this masterserver" % (masterserver.FAILREG_COMMAND, host, port)), True
				else:
					return (("%s server at %s:%d did not reply to info-request (sent to %s:%d)") % (masterserver.FAILREG_COMMAND, host, port, host, port+1)), True
					
		return None, False

