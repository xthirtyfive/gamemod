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

from requestcounter import requestcounter
from debug import debug

# provide the gamemod gui & server list
class guiprovider:
	FILECHECK_INTERVAL = 60*60 # 1h
	
	DBGTAG = "guiprovider"
	DBGTAG_REQUEST = DBGTAG+"/request"
	DBGTAG_REPLY = DBGTAG+"/reply"
	
	LIST_REQUEST = "list"
	READABLELIST_REQUEST = "readablelist"

	def __init__(self, reqfunc):
		self.reqfunc = reqfunc
		self.counter = requestcounter()
		
	def request(self, readable=False):
		return self.reqfunc(readable)
	
	def onrequest(self, line, addr, build): # return (reply, close)
		if line == guiprovider.LIST_REQUEST:
			debug.msg(guiprovider.DBGTAG_REQUEST, "%s request from %s:%d (%sbuild)" % ((line,)+addr+("" if build else "don't ",)))
			self.counter.add(addr[0])
			s = (self.request() if build else True)
			debug.msg(guiprovider.DBGTAG_REQUEST, "sending reply to %s request to %s:%d" % ((line,)+addr))
			return s, True
		elif line == guiprovider.READABLELIST_REQUEST:
			debug.msg(guiprovider.DBGTAG_REQUEST, "%s request from %s:%d (%sbuild)" % ((line,)+addr+("" if build else "don't ",)))
			s = (self.request(True) if build else True)
			debug.msg(guiprovider.DBGTAG_REQUEST, "sending reply to %s request to %s:%d" % ((line,)+addr))
			return s, True
		return None, False
	
	def differentips(self):
		return self.counter.differentips()
	
	def requests(self):
		return self.counter.requests()
