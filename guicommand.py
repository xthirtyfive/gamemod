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

import types

import tools
import config

commands = {
	"vc": "//",
	"clear": "^fr",
	"green": "^fs^f0",
	"blue": "^fs^f1",
	"yellow": "^fs^f2",
	"red": "^fs^f3",
	"grey": "^fs^f4",
	"magenta": "^fs^f5",
	"orange": "^fs^f6",
	"white": "^fs^f7",
	"newline": "\n",
	"listenport": str(config.LISTEN_PORT),
	"ownaddress": config.OWN_ADDRESS
}

class guicommand:
	@staticmethod
	def get(g, cmd_, args, standalone=True):
		cmd = cmd_.lower()
		try:
			return ((commands[cmd](g, args, standalone), None) if (type(commands[cmd]) == types.ClassType or type(commands[cmd]) == types.FunctionType) else (commands[cmd], None)) if commands.has_key(cmd) else (None, "command \"%s\" not found" % cmd)
		except guicommanderror as e:
			return None, str(e)

	@staticmethod
	def args_whole(cmd_): # check if command cmd requires args to be joined toghether
		cmd = cmd_.lower()
		try:
			return commands.has_key(cmd) and commands[cmd].ARGS_WHOLE
		except:
			return False

	@staticmethod
	def args_min(cmd_): # return the minimum number of required arguments for this command
		cmd = cmd_.lower()
		try:
			if commands.has_key(cmd): return commands[cmd].ARGS_MIN
		except:
			return 0

	@staticmethod
	def args_guiline(cmd_): # check if command arguments should be provided as guiline
		cmd = cmd_.lower()
		try:
			return commands.has_key(cmd) and commands[cmd].ARGS_GUILINE
		except:
			return False


class guicommanderror:
	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return self.msg


# --- command section ---

class servercount:
	def __init__(self, g, args, standalone):
		self.g = g
	def __str__(self):
		return str(self.g.registeredservers.len())
commands["servercount"] = servercount

class forservers:
	ARGS_GUILINE = True # arguments should be provided as guiline (which can then contain guicommands again)
	ARGS_WHOLE = True

	def __init__(self, g, args, standalone):
		self.g = g
		self.guiline = args[0]
	def __str__(self):
		s = ""
		if self.g.gui.readablereq:
			for server in self.g.registeredservers.releasingiterator():
				s += (self.guiline.__str__(server) + "\n")
		else:
			for server in self.g.registeredservers.releasingiterator():
				s += self.guiline.__str__(server)
		return s
commands["forservers"] = forservers

class ip:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return server.host
commands["ip"] = ip

class port:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.port)
commands["port"] = port

class escapedesc:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(tools.filterserverdesc(server.desc))
commands["escapedesc"] = escapedesc

class clients:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.numclients)
commands["clients"] = clients

class maxclients:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.maxclients)
commands["maxclients"] = maxclients

class escapeplayerlist:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		s = ""
		space = False
		for (cn, client) in server.clients.iterator():
			s += (" " if space else "") + tools.filterclientname(client.name)
			space = True
		return s
commands["escapeplayerlist"] = escapeplayerlist

class escapedetailplayerlist:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		s = ""
		space = False
		for (cn, client) in server.clients.iterator():
			s += ('%s"%s %d %s %d %d"' % ((" " if space else ""), tools.filterclientname(client.name), cn, tools.filterclientteam(client.team), client.priv, client.state))
			space = True
		return s
commands["escapedetailplayerlist"] = escapedetailplayerlist

class mastermode:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.mastermode)
commands["mastermode"] = mastermode

class map:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return tools.filtermap(server.map)
commands["map"] = map

class gamemode:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.gamemode)
commands["gamemode"] = gamemode

class remaining:
	def __init__(self, g, args, standalone):
		if standalone: raise guicommanderror("can not stand alone")
	def __str__(self, server):
		return str(server.getremaining())
commands["remaining"] = remaining

class sumselfreg:
	N = 0
	def __init__(self, g, args, standalone):
		self.set = None
		self.out = False
		if len(args) and args[0].lower() == "reset":
			self.set = 0
		elif len(args) and args[0].lower() == "out":
			self.out = True
		elif standalone:
			raise guicommanderror("can not stand alone without either \"reset\" or \"out\" as argument")
	def __str__(self, server=None):
		if self.set != None:
			sumselfreg.N = self.set
		elif self.out:
			return str(sumselfreg.N)
		elif server.selfreg:
			sumselfreg.N += 1
		return ""
commands["sumselfreg"] = sumselfreg

class sumnumclients:
	N = 0
	def __init__(self, g, args, standalone):
		self.set = None
		self.out = False
		if len(args) and args[0].lower() == "reset":
			self.set = 0
		elif len(args) and args[0].lower() == "out":
			self.out = True
		elif standalone:
			raise guicommanderror("can not stand alone without either \"reset\" or \"out\" as argument")
	def __str__(self, server=None):
		if self.set != None:
			sumnumclients.N = self.set
		elif self.out:
			return str(sumnumclients.N)
		elif server.numclients > 0:
			sumnumclients.N += server.numclients
		return ""
commands["sumnumclients"] = sumnumclients

class summaxclients:
	N = 0
	def __init__(self, g, args, standalone):
		self.set = None
		self.out = False
		if len(args) and args[0].lower() == "reset":
			self.set = 0
		elif len(args) and args[0].lower() == "out":
			self.out = True
		elif standalone:
			raise guicommanderror("can not stand alone without either \"reset\" or \"out\" as argument")
	def __str__(self, server=None):
		if self.set != None:
			summaxclients.N = self.set
		elif self.out:
			return str(summaxclients.N)
		elif server.maxclients > 0:
			summaxclients.N += server.maxclients
		return ""
commands["summaxclients"] = summaxclients

class sumactiveservers:
	N = 0
	def __init__(self, g, args, standalone):
		self.set = None
		self.out = False
		if len(args) and args[0].lower() == "reset":
			self.set = 0
		elif len(args) and args[0].lower() == "out":
			self.out = True
		elif standalone:
			raise guicommanderror("can not stand alone without either \"reset\" or \"out\" as argument")
	def __str__(self, server=None):
		if self.set != None:
			sumactiveservers.N = self.set
		elif self.out:
			return str(sumactiveservers.N)
		elif server.numclients > 0:
			sumactiveservers.N += 1
		return ""
commands["sumactiveservers"] = sumactiveservers




class primcolor:
	ARGS_WHOLE = True
	s = "^fs^f6"
	def __init__(self, g, args, standalone):
		if len(args):
			self.set = "^fs^f"+args[0]
		else:
			self.set = None

	def __str__(self):
		if self.set:
			primcolor.s = self.set
			return ""
		else:
			return primcolor.s
commands["primcolor"] = primcolor

class guidebug:
	ENABLE = False
	def __init__(self, g, args, standalone):
		self.set = False
		if len(args):
			try:
				self.set = int(args[0]) > 0
			except:
				self.set = True if args[0].lower() != "false" else False
	def __str__(self):
		guidebug.ENABLE = self.set
		return ""
commands["guidebug"] = guidebug

class ifguidebug:
	ARGS_WHOLE = True
	N = 0
	def __init__(self, g, args, standalone):
		if len(args):
			if args[0].lower() == "reset":
				ifguidebug.N = 0
				self.s = ""
			else:
				self.s = args[0]
		else:
			self.s = ("echo \"debug %d, line %d\";" % (ifguidebug.N, g.gui.curline))
			ifguidebug.N += 1

	def __str__(self):
		return self.s if guidebug.ENABLE else ""
commands["ifguidebug"] = ifguidebug

class guisizecallf:
	ARGS_WHOLE = True
	ARGS_MIN = 1
	def __init__(self, g, args, standalone):
		if not args[0].count("%d") == 1: raise guicommanderror("argument requires exactly one \"%d\"")
		self.g = g
		self.s = args[0]
	def __str__(self):
		n = self.g.gui.curreqlen + (len(self.s) - 2) # 2nd added value = length of self.s without "%d"
		n_len = len(str(n)) # say n is 999: n_len would be 3.
		while len(str(n+n_len)) > n_len: # now len(str(999+3)) would be len("1002") = 4... 4 is > than 3. increase n_len until they are equal.
			n_len += 1
		return self.s % (n+n_len)
commands["guisizecallf"] = guisizecallf

class differentips:
	def __init__(self, g, args, standalone):
		self.g = g
	def __str__(self):
		return str(self.g.guiprovider.differentips())
commands["differentips"] = differentips

class requests:
	def __init__(self, g, args, standalone):
		self.g = g
	def __str__(self):
		return str(self.g.guiprovider.requests())
commands["requests"] = requests

class pass_:
	ARGS_WHOLE = True
	ARGS_MIN = 1
	def __init__(self, g, args, standalone):
		self.s = args[0]
	def __str__(self):
		return self.s
commands["pass"] = pass_

class version:
	ARGS_WHOLE = True
	SV = "0"
	def __init__(self, g, args, standalone):
		self.g = g
		if len(args):
			version.SV = args[0]
			self.mute = True
		else:
			self.mute = False
	def __str__(self):
		if not self.mute:
			return ("%s-%s" % (self.g.version, version.SV))
		else:
			return ""
commands["version"] = version
