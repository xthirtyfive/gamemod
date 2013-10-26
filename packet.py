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

from buf import buf

class packet:
	PING_BYTE = "\x01"
	EXTINFO_BYTE = "\x00"
	ALTEXTINFO_BYTE = "\x64"
	
	EXT_VERSION = 105
	EXT_ACK = -1
	EXT_NO_ERROR = 0
	EXT_ERROR = 1
	EXT_PLAYERSTATS_RESP_IDS = -10
	EXT_PLAYERSTATS_RESP_STATS = -11
	EXT_UPTIME = 0
	EXT_PLAYERSTATS = 1
	EXT_TEAMSCORE = 2
	
	EXTINFOPLAYERSTATS_DATA = EXTINFO_BYTE + chr(buf.unsigned(EXT_PLAYERSTATS)) + "\xff"	# \xff = -1 = cn (all clients)
	ALTEXTINFOPLAYERSTATS_DATA = ALTEXTINFO_BYTE + chr(buf.unsigned(EXT_PLAYERSTATS)) + "\xff"	# \xff = -1 = cn (all clients)
	
	PING_DATA = PING_BYTE
	EXTINFO_DATA = EXTINFOPLAYERSTATS_DATA
	ALTEXTINFO_DATA = ALTEXTINFOPLAYERSTATS_DATA

	@staticmethod
	def pingpacket(addr):
		return packet(packet.PING_DATA, addr)
	
	@staticmethod
	def extinfopacket(addr):
		return packet(packet.EXTINFO_DATA, addr)
	
	@staticmethod
	def altextinfopacket(addr):
		return packet(packet.ALTEXTINFO_DATA, addr)
	
	# ---
	
	def __init__(self, data_, addr_=None):
		self.data = data_
		self.addr = addr_
