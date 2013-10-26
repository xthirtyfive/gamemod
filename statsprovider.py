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

import json

import guicommand
from debug import debug

class statsprovider:
	DBGTAG = "statsprovider"
	DBGTAG_REQUEST = DBGTAG+"/request"
	
	STATS_REQUEST = "stats"

	def __init__(self, g):
		self.g = g
		self.versioncommand = guicommand.version(g, [], True)
		
	def jsonstats(self):
		sumclients = 0
		summaxclients = 0
		usedservers = 0
		directregservers = 0
		suggestedservers = 0
		for s in self.g.registeredservers.releasingiterator():
			if s.numclients > 0:
				sumclients += s.numclients
				usedservers += 1
			if s.maxclients > 0: summaxclients += s.maxclients
			if s.selfreg: directregservers += 1
			if s.suggested: suggestedservers += 1
		i = {
			"requests": self.g.guiprovider.requests(),
			"different_ips": self.g.guiprovider.differentips(),
			"clients_online": sumclients,
			"clients_space": summaxclients,
			"servers_online": self.g.registeredservers.len(),
			"servers_used": usedservers,
			"servers_directreg": directregservers,
			"servers_suggested": suggestedservers,
			"version": str(self.versioncommand)
		}
		return json.dumps(i)
	
	def onrequest(self, line, addr, build):
		if line == statsprovider.STATS_REQUEST:
			debug.msg(statsprovider.DBGTAG_REQUEST, "%s request from %s:%d" % ((line,)+addr))
			return self.jsonstats(), True
