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
from guiline import guiline

# read gui from file and build list of guilines
class gui:
	DBGTAG = "gui"
	DBGTAG_ERROR = DBGTAG+"/error"
	DBGTAG_ERRORS = DBGTAG+"/errors"
	DBGTAG_WARNING = DBGTAG+"/warning"
	DBGTAG_WARNINGS = DBGTAG+"/warnings"
	
	
	GUICOMMAND_PREFIX = "?*"
	GUICOMMAND_ARGS_PREFIX = "("
	GUICOMMAND_ARGS_SUFFIX = ")"
	GUICOMMAND_ARGS_SEPERATOR = " "
	
	ARGS_NOMODIFIERS_MODIFIER = "NOMODIFIERS "
	ARGS_TILEOL_MODIFIER = "TILEOL "
	ARGS_WHOLE_MODIFIER = "WHOLE "

	def __init__(self, g):
		self.curreqlen = 0
		self.curline = 0
		self.path = "gui.cfg" # TODO
		self.g = g
		self.guilines = lockedlist()
	
	def load(self):
		self.update(False)
	
	def update(self, catch=True, force=False):
		# update gui (read it from file)
		try:
			f = open(self.path, "r")
			newguilines = []
			errors = []
			warnings = []
			n = 0 # line number
			for line in f:
				n += 1
				self.curline = n
				gl = guiline(self.g, line[:-1] if (len(line) > 0 and line[-1]=="\n") else l)
				for w in gl.warnings:
					warnings.append("warning in line %d: %s" % (n, w))
				if gl.error: errors.append("skipping line %d: %s" % (n, gl.error))
				else: newguilines.append(gl)
			f.close()
			exchange = force or (not len(errors))
			
			for w in warnings:
				debug.msg(gui.DBGTAG_WARNING, w)
			debug.msg(gui.DBGTAG_WARNINGS, "%s warnings while reading gui" % (str(len(warnings)) if len(warnings) else "no"))
			
			for e in errors:
				debug.msg(gui.DBGTAG_ERROR, e)
			debug.msg(gui.DBGTAG_ERRORS, "%s errors while reading gui%s, %s" % (str(len(errors)) if len(errors) else "no", " (ignoring these lines)" if len(errors) else "", "applying new guilines list" if exchange else "cancelling update"))
			
			if exchange:
				self.guilines.exchange(newguilines)
			return exchange, "%d lines read, %d errors (skipping lines with errors), %d warnings" % (len(newguilines), len(errors), len(warnings))
			
		except:
			try: f.close()
			except: pass
			if catch: debug.exc(self)
			else: raise
		return False, "internal errors occurred"
			
	
	def onrequest(self, readable=False):
		c = True
		for line in self.guilines.iterator():
			if c: # weird logic because self.guilines is locked (and therefore parallel calls to onrequest will block) in this loop only, not outside
				self.curreqlen = 0
				self.readablereq = readable
				c = False
			s = str(line)
			self.curreqlen += len(s)
			if readable:
				if len(s) or (not line.numparts): # only send if line is not empty (len(s)) or was empty in file too (not line.numparts)
					yield line.getleadingwhitespaces()
					yield s
					yield "\n"
			else:
				yield s
			
			
