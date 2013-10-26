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

def escape(s):
	return s.replace("^", "^^").replace("\"", "^\"")

def replacequotes(s):
	return s.replace("\"", "'")

def delroofs(s):
	return s.replace("^", "")

def delcolors(s):
	while True:
		i = s.find("\f")
		if i < 0: break
		s = s.replace(s[i:i+2], "")
	return s

def delspaces(s):
	return s.replace(" ", "").replace("\t", "")

def safe(s):
	return delcolors(replacequotes(delroofs(s)))

def safename(s):
	return safeword(s)

def safeword(s):
	return delspaces(safe(s))
