import requests
import os
import sys
import re
import ipaddress

from datetime import date
from zipfile import ZipFile

class GoatJockey():
	'''
	'''
	_ALEXA_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
	_ETLD_URL = 'http://publicsuffix.org/list/public_suffix_list.dat'

	def __init__(self, topx=5048, alexa_path='./top-1m.csv.zip', whitelist_path='./whitelist.dat', etld_path='./public_suffix_list.dat'):
		self._ALEXA_PATH = alexa_path
		self._WHITELIST_PATH = whitelist_path
		self._ETLD_PATH = etld_path

		# Some validation. If topx is greater than 1m, it'll throw an error.
		if topx > 1000000:
			topx = 1000000
		self.refresh_lists(topx=topx)

		self.hash_pattern = re.compile('([a-fA-F0-9]{64}$|[a-fA-F0-9]{40}$|[a-fA-F0-9]{32}$)')

	def _download_file(self, url, fpath, blocksize=1024):
		'''
		'''
		r = requests.get(url)
		with open(fpath, 'wb') as f:
			for block in r.iter_content(blocksize):
				f.write(block)

	def _is_old_file(self, fpath):
		'''
		'''
		try:
			mtime = os.path.getmtime(fpath)
		except OSError:
			return True

		if date.fromtimestamp(mtime) < date.today():
			return True

		return False

	def refresh_lists(self, topx=5048):
		'''
		'''
		if self._is_old_file(self._ALEXA_PATH):
			self._download_file(self._ALEXA_URL,
						self._ALEXA_PATH)
		self.parse_alexa(limit=topx)
		if self._is_old_file(self._ETLD_PATH):
			self._download_file(self._ETLD_URL,
						self._ETLD_PATH)
		self.parse_etld()
		self.parse_whitelist()

	def parse_alexa(self, limit=5048):
		'''
		'''
		with ZipFile(self._ALEXA_PATH, 'r') as archive:
			with archive.open(archive.namelist()[0], 'r') as f:
				# Read only what is absolutely needed based on limit
				lines = [next(f) for line in range(limit)]

		alexa = {}
		for line in lines:
			line = line.decode(sys.getdefaultencoding())
			line = line.split(',')[1]
			line = line.strip()

			alexa[line] = line

		self.ALEXA_DOMAINS = alexa

	def parse_whitelist(self):
		'''
		'''
		try:
			with open(self._WHITELIST_PATH) as f:
				lines = [line for line in f.readlines()]
		except IOError:
			self.WHITELIST = {}
			return

		whitelist = {}
		for line in lines:
			#line = line.decode(sys.getdefaultencoding())
			line = line.strip()

			whitelist[line] = line

		self.WHITELIST = whitelist

	def parse_etld(self):
		'''
		'''

		normal = set()
		wildcard = set()
		special = set()

		with open(self._ETLD_PATH, 'rb') as f:
			for line in f:
				line = line.decode('utf-8')
				if not line or line.startswith('//'):
					continue

				line = line.strip()
				if line.startswith('*'):
					wildcard.add(line[2:])

				elif line.startswith('!'):
					special.add(line[1:])
				else:
					normal.add(line)

		self.NORMAL_TLDS = normal
		self.WILDCARD_TLDS = wildcard
		self.SPECIAL_TLDS = special

	def get_tld(self, domain):
		'''Parse out the effective TLD. 
		This prevents things like www.google.com escaping filtering.
		'''

		parts = domain.split('.')
		tld = None

		for i in range(len(parts)):
			prev_tld = tld
			tld = '.'.join(parts[i:])

			if tld in self.SPECIAL_TLDS:
				return (parts[i], '.'.join(parts[i+1]))

			elif i >= 1 and tld in self.NORMAL_TLDS:
				return (parts[i-1], tld)

			elif i >= 2 and tld in self.WILDCARD_TLDS:
				if prev_tld not in self.SPECIAL_TLDS:
					return(parts[i-2], prev_tld)

		return None

	def _ip_match(self, ipaddr):
		'''This exists for future support, it always returns False
		for now.
		'''
		return False, str(ipaddr)

	def _hash_match(self, ahash):
		'''This exists for future support, it always returns False
		for now.
		'''
		return False, ahash

	def _domain_match(self, domain):
		'''
		'''
		tld = '.'.join(self.get_tld(domain))
		if tld in self.ALEXA_DOMAINS:
			return True, self.ALEXA_DOMAINS[tld]
		if tld in self.WHITELIST:
			return True, self.WHITELIST[tld]
		return False, tld

	def match(self, ioc):
		'''
		'''
		ioc = ioc.lower()
		# Try IP address first, this is an easy check based on whether or not
		# the ipaddress library outputs an error on parsing attempts
		try:
			ip = ipaddress.ip_address(ioc)
			return self._ip_match(ip)
		except ValueError:
			pass

		# Next check for hashes, the pattern currently checks for SHA-1,
		# SHA-256, and MD5
		if self.hash_pattern.match(ioc):
			return self._hash_match(ioc)

		# Finally, try looking up the ioc as a domain
		try:
			return self._domain_match(ioc)
		except TypeError:
			return False, None

		return False, None