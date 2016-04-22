#!/usr/bin/env python2.7

import sys
import string
import random
import hashlib
import itertools

#constatss

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = int(sys.argv[1])
#ATTEMPTS = int(sys.argv[2]) cause doing it systematically
HASHES = sys.argv[3]


#Utility functions

def usage(exit_code=0):
	print >>sys.stderr, '''Usage: hulk.py [-a ALPHABET -l LENGTH -s HASHES -p PREFIX]

Options:

      -a  ALPHABET    Alphabet used for passwords
      -l  LENGTH      Length for passwords
      -s  HASHES      Path to file containing hashes
      -p  PREFIX      Prefix to use for each candidate password
'''
	sys.exit(exit_code)

def md5sum(s):
	return hashlin.md5(s).hexdigest()

# Parsing the command line


#Main Exacution

if __name__ == '__main__':
	hashes = set([l.strip() for l in open(HASHES)])
	found = set()

	for canidate in itertools.prodcut(ALPHABET, repeat=LENGTH):
		canidate = ''.join(canidate)
		#canidate = ''.join([random.choice(ALPHABET) for _ in range(LENGHT)])

		print canidate

		checksum = md5sum(candiate)
		if checksum in hashes:
			found.add(candidate)

	for word in sorted(found):
		print word