#!/usr/bin/env python2.7

import getopt
import os
import sys
import fnmatch
import re

# Global Variables

TYPE = ""
executable = False
readable = False
writable = False
empty = False

NAME = ""
PATH = ""
REGEX = ""

MODE = 0
FILE = ""

n = ''
gn = ''

# Functions

def error(message, exit_code=1):
    print >>sys.stderr, message
    sys.exit(exit_code)


def usage(status=0):
    	print '''usage: find.py directory [options]...

Options:

    -type [f|d]     File is of type f for regular file or d for directory

    -executable     File is executable and directories are searchable to user
    -readable       File readable to user
    -writable       File is writable to user

    -empty          File or directory is empty

    -name  pattern  Base of file name matches shell pattern
    -path  pattern  Path of file matches shell pattern
    -regex pattern  Path of file matches regular expression

    -perm  mode     File's permission bits are exactly mode (octal)
    -newer file     File was modified more recently than file

    -uid   n        File's numeric user ID is n
    -gid   n        File's numeric group ID is n'''.format(os.path.basename(sys.argv[0]))
    	sys.exit(status)

def include(path):

	broken = False

	try:
		statinfo = os.stat(path)
	except OSError:
		statinfo = os.lstat(path)
		broken = True

	if TYPE == "f":
		if not os.path.isfile(path):
			return False

	elif TYPE == "d":
		if not os.path.isdir(path):
			return False

	if executable:
		if not os.access(path, os.X_OK):
			return False

	if readable:
		if not os.access(path, os.R_OK):
			return False
	
	if writable:
		if not os.access(path, os.W_OK):
			return False

	if empty:
		if os.path.islink(path) and broken:
			return False
		elif os.path.isfile(path):
			if statinfo.st_size !=0:
				return False
		elif os.path.isdir(path):
			try:
				if os.listdir(path) != []:
					return False
			except OSError:
				return False

	if NAME != "":
		if not fnmatch.fnmatch(os.path.basename(path), NAME):
			return False

  if PATH != "":
    if not fnmatch.fnmatch(path, PATH):
      return False

	if REGEX != "":
    if not re.search(REGEX, path):
      return False


	if MODE != 0:
		if MODE != int(str(oct(statinfo.st_mode))[-3:]):
			return False
	
	if FILE != '':
		if statinfo.st_mtime <= os.stat(FILE).st_mtime:
			return False

	if n != '':
		if int(statinfo.st_uid) != int(n):
			return False

	if gn != '':
		if int(statinfo.st_gid) != int(gn):
			return False	

	return True

# Parse command line options

args= list('')

directory = ' '.join(sys.argv[1:]).split('-')[0].replace(' ', '')

for arg in sys.argv[2:]:
	if arg[0] == '-':
		arg = arg.split('-')[1]
		if arg == 'h':
			usage(1)
		else:
			args.append(arg)
	else:
		args.append(arg)

count = 0

while count < len(args):
	if args[count] == 'type':
		TYPE = args[int(count) + 1]
		count = count + 1
	elif args[count] == 'executable':
		executable = True
  elif args[count] == 'readable':
    readable = True
  elif args[count] == 'writable':
    writable = True
  elif args[count] == 'empty':
    empty = True
	elif args[count] == 'name':
		NAME = args[int(count) + 1]
		count = count + 1
  elif args[count] == 'path':
    PATH = args[int(count) + 1]
		count = count + 1
  elif args[count] == 'regex':
    REGEX = args[int(count) + 1]
		count = count + 1
	elif args[count] == 'perm':
		MODE = int(args[int(count) + 1])
		count = count + 1
	elif args[count] == 'newer':
		FILE = args[int(count) + 1]
		count = count + 1
	elif args[count] == 'uid':
		n = args[int(count) + 1]
		count = count + 1
	elif args[count] == 'gid':
		gn = args[int(count) + 1]
		count = count + 1
	else:
		usage(1)
	
	count = count + 1

# main

if include(directory):
	print directory

for root, dirs, files in os.walk(directory, followlinks=True):

	for name in dirs + files:
		
		stream = os.path.join(root,name)
		
		if include(stream):
			print stream
