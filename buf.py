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

class EndOfBufError(Exception):
	def __init__(self):
		pass

class buf:
	
	@staticmethod
	def signed(n):
		if n > 127:
			return n - 256
		else:
			return n
	
	@staticmethod
	def unsigned(n):
		if n < 0:
			return n + 256
		else:
			return n
			
	# ---
	
	def __init__(self, data_):
		self.data = data_
		self.i = 0
		
	def len(self):
		return len(self.data)
	
	def pos(self):
		return self.i
		
	def seek(self, pos):
		self.i = min(pos, len(self.data))
	
	def skip(self, n):
		self.seek(self.i+n)
	
	def available(self):
		return self.len() - self.i
	
	def read(self):
		if not self.i < len(self.data):
			raise EndOfBufError
		n = self.data[self.i]
		self.i += 1
		return ord(n)
	
	def readstring(self, n):
		n = min(n, self.available())
		if n:
			s = self.data[self.i : self.i+n]
			self.i += n
		return s
	
	# ---
	
	def getint(self):
		c = self.read()
		if c == 0x80:
			n = self.read()
			n |= (buf.signed(self.read()) << 8)
			return n
		elif c == 0x81:
			n = self.read()
			n |= (self.read() << 8)
			n |= (self.read() << 16)
			n |= (self.read() << 24)
			return n
		else:
			return buf.signed(c)

	def getstring(self):
		s = ""
		while self.available():
			c = self.getint()
			if not c: break
			if c >= 0 and c < 256: s += chr(c)
		return s
			
			
			
			
			
