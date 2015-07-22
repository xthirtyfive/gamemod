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

import time
import sys

from log import log
from debug import debug
from serverlist import serverlist
from masterclient import masterclient
from additionalservers import additionalservers
from gui import gui
from masterserver import masterserver
from guiprovider import guiprovider
from netserver import netserver
from servercommunicator import servercommunicator
from statsprovider import statsprovider

# gamemod v5 (Aug 2012)

class gamemod:

	VERSION = "5.0k"

	def __init__(self):
		self.version = gamemod.VERSION

		self.bannedservers = serverlist()
		self.registeredservers = serverlist(banned=self.bannedservers)
		self.pendingservers = serverlist(banned=self.bannedservers)

		self.masterclient = masterclient(self.pendingservers) # fetch gameservers from sauerbraten.org

		self.additionalservers = additionalservers(self.registeredservers, self.pendingservers, self.bannedservers) # fetch additional gameserver from servers.cfg and ban servers in banned.cfg
		self.additionalservers.load()

		self.gui = gui(self)
		self.gui.load()

		self.masterserver = masterserver(self.registeredservers, self.pendingservers) # let gameservers register at this (regserv) and let gameservers be registered by someone else (suggest)
		self.guiprovider = guiprovider(self.onguirequest) # provide the gamemod gui & server list
		self.statsprovider = statsprovider(self) # provide access to stats via additional commands

		# listen for connections from both clients requesting list of servers and servers trying to register and forward them to all functions in list respectively, until one of them returns a reply
		self.netserver = netserver([self.onrequest, self.masterserver.onrequest, self.guiprovider.onrequest, self.statsprovider.onrequest])

		# ping servers and kick them out if they time out / add pending servers as registered if they reply in time
		# handle replies from servers
		self.servercommunicator = servercommunicator(self.registeredservers, self.pendingservers)

	def onguirequest(self, *args):
		# called when the guiprovider needs the gui to be built
		self.registeredservers.sort()
		return self.gui.onrequest(*args)

	def onrequest(self, line, addr, build):
		if addr[0] == "127.0.0.1":
			forceupdategui = line == "forceupdategui"
			if forceupdategui or line == "updategui":
				succ, msg = self.gui.update(force=forceupdategui)
				return ("gui updated successfully: %s" if succ else "could not update gui: %s") % msg, True

			elif line == "updateservers":
				succ, msg = self.additionalservers.updateservers()
				return ("servers updated successfully: %s" if succ else "could not update servers: %s") % msg, True

			elif line == "updatebanned":
				succ, msg = self.additionalservers.updatebanned()
				return ("banned servers updated successfully: %s" if succ else "could not update banned servers: %s") % msg, True

			elif line == "exc":
				(0 + "s")
				return "exception has been raised", False

			elif line == "catchexc":
				try:
					(0 + "s")
				except:
					debug.exc()
				return "raised exception has been caught", False

		return None, False



def main():
	debug.msg(True, "--- gamemod masterserver %s starting up ---" % gamemod.VERSION)

	g = gamemod()
	try:
		while True: time.sleep(1) # TODO
	except KeyboardInterrupt:
		msg = "exiting (KeyboardInterrupt) ...";
		try:
			debug.msg(True, msg)
		except:
			try: log.out("(debug.msg failed, using log.out) " + msg)
			except: print("(debug.msg and log.out failed, using print) " + msg)
		sys.exit()

main()
