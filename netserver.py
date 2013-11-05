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
from accesscache import accesscache
from replycache import replycache
import config

import threading
import socket
import types

# listen for connections from both clients requesting list of servers and servers trying to register and forward them to all functions in list respectively, until one of them returns a reply
class netserver:
	DBGTAG = "netserver"
	DBGTAG_TRAFFIC = DBGTAG+"/traffic"
	DBGTAG_UNKNOWN = DBGTAG+"/unknown"
	DBGTAG_EMPTYLINE = DBGTAG+"/emptyline"
	DBGTAG_REPLY = DBGTAG+"/reply"
	DBGTAG_REPLYTEXT = DBGTAG+"/replytext"
	DBGTAG_FORCECLOSE = DBGTAG+"/forceclose"
	DBGTAG_REJECT = DBGTAG+"/reject"
	DBGTAG_RECVFAIL = DBGTAG+"/recvfail"
	DBGTAG_SENDFAIL = DBGTAG+"/sendfail"

	def __init__(self, funcs):
		self.addr = config.LISTEN_ADDR
		self.port = config.LISTEN_PORT
		
		self.accesscache = accesscache(config.MAX_CONNECTIONS_PER_IP)
		
		self.cache = replycache()
		
		self.thread = threading.Thread(target=self.run, args=(funcs,))
		self.thread.daemon = True
		self.thread.start()
	
	def send(self, sock, reply, record = False): # returns: (replytext(str/None), n(int), err(bool))
		replytext = ("" if record else None)

		if type(reply) != types.GeneratorType:
			reply = [reply]
		
		n = 0
		err = False
		for seq in reply:
			n += len(seq)
			try: sock.send(seq)
			except:
				err = True
				break
			if replytext != None: replytext += seq
		
		if not err:
			sock.send("\n")
			if replytext != None: replytext += "\n"
			n += 1 # +1 for \n
		
		return replytext, n, err
	
	def recv(self, sock): # returns (lines(list/None), err(bool))
		s = ""
		while len(s) <= 0 or s[-1] != "\n": # wait until we've got something with a \n as last byte
			try:
				r = sock.recv(4096)
			except:
				return None, True
				
			if (not r) or (len(r) <= 0):
				return None, True
			else:
				s += r
			
		# now that we've got something with a \n as last byte, split it on \n and loop through each line
		lines = s[:-1].split("\n") # s[:-1] - cut off the last \n
		return lines, False

	def processconnection(self, i, funcs):
		(sock, addr) = i
		(host, port) = addr

		debug.msg(netserver.DBGTAG, "connection from %s:%d" % (host, port))
		
		sock.settimeout(2)
	
		closecon = False
		try:
			while True:
				lines, err = self.recv(sock)
				
				if err:
					debug.msg(netserver.DBGTAG_RECVFAIL, "an error occured while receiving request from %s:%d" % (host, port))
					break
				
				for line in lines:
				
					if len(line) <= 0:
						debug.msg(netserver.DBGTAG_EMPTYLINE, "empty line received from %s:%d, skipping" % (host, port))
						continue
		
					debug.msg(netserver.DBGTAG_TRAFFIC, "received from %s:%d: %s" % (host, port, line))
	
					reply = None
					close = False
					cachedreply = self.cache.find(line)
					
					build = not bool(cachedreply)
					for func in funcs:
						r = func(line, addr, build)
						if not r: continue
						(creply, cclose) = r
						if build: (reply, close) = r
						if creply or cclose: break
					
					if cachedreply:
						(reply, close) = cachedreply
					
					closecon = closecon or close
				
					if reply:
						replytext, n, err = self.send(sock, reply, (debug.tagenabled(netserver.DBGTAG_REPLYTEXT) or ((not cachedreply) and replycache.enabled(line))))
					
						if not err:
							debug.msg(netserver.DBGTAG_REPLY, "sent %sreply with length %d to %s:%d" % (("cached " if cachedreply else ""), n, host, port))
							if replytext != None: debug.msg(netserver.DBGTAG_REPLYTEXT, "sent %sreply to %s:%d: (starts next line)\n%s\n --- end of reply ---" % (("cached " if cachedreply else ""), host, port, replytext))
						
							if (not cachedreply) and replycache.enabled(line): self.cache.cache(line, replytext, close)
						else:
							debug.msg(netserver.DBGTAG_SENDFAIL, "an error occured while sending reply to %s:%d" % (host, port))
						
					elif close: # no reply, but close - forceclose
						debug.msg(netserver.DBGTAG_FORCECLOSE, "force-closing connection to %s:%d without reply" % (host, port))
						break
					else:
						debug.msg(netserver.DBGTAG_UNKNOWN, "no reply available for line received from %s:%d: %s" % (host, port, line))
					
				if closecon: break
		except:
			debug.msg(netserver.DBGTAG, "an error occured while processing connection with %s:%d" % (host, port))
			debug.exc()
			
		self.accesscache.end(host)

		shut = False
		try:
			sock.shutdown(socket.SHUT_RDWR)
			shut = True
		except: pass # remote has already shut down connection
		try:
			sock.close()
		except: pass
		
		debug.msg(netserver.DBGTAG, "connection %s:%d closed (shutdown %s)" % (host, port, "succeeded" if shut else "failed"))

	def run(self, funcs):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((self.addr, self.port))
		sock.listen(5)
		
		while True:
			try:
				i = sock.accept()
				
				if self.accesscache.permit(i[1][0]):
					tt = threading.Thread(target=self.processconnection, args=(i, funcs))
					tt.start()
					
				else: # connection not permitted by accesscache
					debug.msg(netserver.DBGTAG_REJECT, "rejecting connection from %s:%d (not permitted by accesscache)" % i[1])
					try:
						i[0].shutdown(socket.SHUT_RDWR)
					except: pass
					try:
						i[0].close()
					except: pass
					
			except:
				debug.exc(self)
