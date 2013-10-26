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
from guicommand import guicommand
import types

class guiline:
	DBGTAG = "guiline"
	DBGTAG_DUMPPARTS = DBGTAG+"/dumpparts"
	DBGTAG_STRPARTERROR = DBGTAG+"/strparterror"
	
	COMMON_END_BYTES = ";["
	GUI_REPLACEMENTS = {
		"\\\"": "^\"", # replace \" with ^"
	}

	def __init__(self, g, s, standalone=True):
		self.warnings = []
		self.g = g
		self.gui = self.g.gui
		self.standalone = standalone # is this a typical guiline (standalone) or is it contained by an argument already in a guicommand (not standalone)?
		self.parts = []
		self.error = self.parse(s, standalone)
		if (not self.error) and len(self.parts) and (type(self.parts[0]) == types.StringType or len(self.parts) != 1):
			for lp in reversed(self.parts):
				if type(lp) == types.StringType:
					rstrip_lp = lp.rstrip()
					if not len(rstrip_lp): continue
					lc = rstrip_lp[-1]
					for b in guiline.COMMON_END_BYTES:
						if b == lc: break
					else:
						self.warnings.append("line does not end in a common character: %s" % s)
				else:
					self.warnings.append("line ends in a guicommand and not in a common character: %s" % s)
				break
		self.numparts = len(self.parts)
				
	
	def parse(self, s, standalone):
		start_i = 0
		while start_i < len(s): # skip whitespaces in front
			b = s[start_i]
			if b != "\t" and b != " ": break
			start_i += 1
		self.leadingwhitespaces = s[:start_i]
		comment_i = s.find("//", start_i)
		if comment_i > -1:
			s = s[:comment_i]
		for i in guiline.GUI_REPLACEMENTS:
			s = s.replace(i, guiline.GUI_REPLACEMENTS[i])
		while True:
			i = s.find(self.gui.GUICOMMAND_PREFIX, start_i)
			if i < 0:
				p = s[start_i:]
				if len(p): self.parts.append(p) # append rest of the line (or the whole line if it does not contain any guicommands)
				break
			argpart_i = s.find(self.gui.GUICOMMAND_ARGS_PREFIX, i+len(self.gui.GUICOMMAND_PREFIX))
			if argpart_i < 0: return "missing arguments-opening \"%s\" after guicommand-prefix \"%s\" and guicommand-name" % (self.gui.GUICOMMAND_ARGS_PREFIX, self.gui.GUICOMMAND_PREFIX)
			cmd = s[i+len(self.gui.GUICOMMAND_PREFIX):argpart_i]
			args_i = argpart_i+len(self.gui.GUICOMMAND_ARGS_PREFIX)
			endargs_i = None
			whole = guicommand.args_whole(cmd)
			while True:
				end = False
				if s.startswith(self.gui.ARGS_NOMODIFIERS_MODIFIER, args_i): # allow no more modifiers
					args_i += len(self.gui.ARGS_NOMODIFIERS_MODIFIER)
					end = True
				elif s.startswith(self.gui.ARGS_TILEOL_MODIFIER, args_i): # read argument until ")" at end of line
					endargs_i = False
					args_i += len(self.gui.ARGS_TILEOL_MODIFIER)
				elif s.startswith(self.gui.ARGS_WHOLE_MODIFIER, args_i): # read whole argument list as one string
					whole = True
					args_i += len(self.gui.ARGS_WHOLE_MODIFIER)
				else: break
				if end: break
			if endargs_i == None: # search for end of args
				endargs_i = s.find(self.gui.GUICOMMAND_ARGS_SUFFIX, args_i)
				if endargs_i < 0: return "missing arguments-closing \"%s\" at end of command" % gui.GUICOMMAND_ARGS_SUFFIX
			elif endargs_i == False: # TILEOL modifier is used
				endargs_i = len(s)-len(self.gui.GUICOMMAND_ARGS_SUFFIX)
				if s[endargs_i:endargs_i+len(self.gui.GUICOMMAND_ARGS_SUFFIX)] != self.gui.GUICOMMAND_ARGS_SUFFIX: return "missing arguments-closing \"%s\" at end of line" % gui.GUICOMMAND_ARGS_SUFFIX
			
			argstring = s[args_i:endargs_i]
			if not len(argstring):
				args = []
			elif whole: # WHOLE modifier is used
				args = [argstring]
			else:
				args = argstring.split(self.gui.GUICOMMAND_ARGS_SEPERATOR)
				
			args_min = guicommand.args_min(cmd)
			if len(args) < args_min and ((not whole) or (not len(args))):
				return "guicommand \"%s\" requires at least %d argument%s" % (cmd, args_min, "s" if args_min > 1 else "")
				
			if guicommand.args_guiline(cmd):
				args_ = []
				for a in args:
					gl = guiline(self.g, a, False)
					if gl.error: return "in argument of guicommand \"%s\": %s" % (cmd, gl.error)
					args_.append(gl)
				args = args_
			
			item, msg = guicommand.get(self.g, cmd, args, standalone) # item may either be a guicommand instance or just a string (in case a guicommand would always result in the same string)
			if item == None:
				return "guicommand \"%s\": %s" % (cmd, msg)
			
			p = s[start_i:i]
			if len(p): self.parts.append(p)
			#self.parts.append("guicommand \"%s\" with %d args: \"%s\"" % (cmd, len(args), "\", \"".join(args)))
			self.parts.append(item)
			start_i = endargs_i+len(self.gui.GUICOMMAND_ARGS_SUFFIX) # start search for next guicommand at position where the last one ended
		
		if debug.tagenabled(guiline.DBGTAG_DUMPPARTS): debug.msg(guiline.DBGTAG_DUMPPARTS, "parsed %d parts: %s" % (len(self.parts), repr(self.parts)))
		
	def getleadingwhitespaces(self):
		return self.leadingwhitespaces
	
	def __str__(self, *args):
		s = ""
		for p in self.parts:
			if type(p) == types.StringType:
				s += p
			else:
				try:
					s += p.__str__(*args)
				except:
					debug.msg(guiline.DBGTAG_STRPARTERROR, "was getting string from guicommand: %s (re-raising this exception)" % repr(p))
					raise
		return s
		

