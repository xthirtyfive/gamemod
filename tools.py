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

import string

def escape(s):
	return s.replace("^", "^^").replace("\"", "^\"")

def replacequotes(s):
	return s.replace("\"", "'")

def delcarets(s):
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
	return delcolors(replacequotes(delcarets(s)))

def safename(s):
	return safeword(s)

def safeword(s):
	return delspaces(safe(s))

ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&()*+,-./:;<=>?@[]_{|}~'

def filterstr(s, spaces = True):
	return "".join(c for c in s if (c in ALLOWED_CHARS or (c == " " and spaces)))

def filterclientname(s):
	return filterstr(s, spaces = False)

def filterclientteam(s):
	return filterstr(s, spaces = False)

def filterserverdesc(s):
	return filterstr(s, spaces = True)

def filtermap(s):
	return filterstr(s, spaces = True)
