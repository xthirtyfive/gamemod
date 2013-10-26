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

from client import client
from threading import Lock

class clientlist:
	
	
	def __init__(self):
		self.list = {}
		self.lock = Lock()
		
	def get(self, cn):
		with self.lock:
			if self.list.has_key(cn):
				return self.list[cn]
			else:
				c = client()
				self.list[cn] = c
				return c
	
	def keep(self, cn=None):
		if cn != None:
			self.get(cn).keep = True
		else:
			with self.lock:
				dellist = []
				for i in self.list:
					c = self.list[i]
					if not c.keep:
						dellist.append(i)
					else:
						c.keep = False
				for i in dellist:
					del self.list[i]
	
	def len(self):
		with self.lock:
			return len(self.list)
	
	def iterator(self):
		with self.lock:
			for cn in self.list:
				yield (cn, self.list[cn])
