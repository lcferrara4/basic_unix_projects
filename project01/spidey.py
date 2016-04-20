#!/usr/bin/env python2.7

import getopt
import logging
import os
import signal
import mimetypes
import socket
import sys

# Constants

ADDRESS  = '0.0.0.0'
PORT     = 9234
FORK = False
BACKLOG  = 0
DOCROOT = '.'
LOGLEVEL = logging.INFO
PROGRAM  = os.path.basename(sys.argv[0])

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: {program} [-d DOCROOT -p PORT -f -v]

Options:

    -h       Show this help message
    -v       Set logging to DEBUG level
    -f       Enable forking mode

    -d DOCROOT  Set root directory (default is current)
    -p PORT     TCP Port to listen to (default is 9234)
'''.format(program=PROGRAM)
    sys.exit(exit_code)

# BaseHandler Class

class BaseHandler(object):

    def __init__(self, fd, address,docroot):
        ''' Construct handler from file descriptor and remote client address '''
        self.logger  = logging.getLogger()        # Grab logging instance
        self.socket  = fd                         # Store socket file descriptor
        self.address = '{}:{}'.format(*address)   # Store address
        self.docroot = os.path.abspath(docroot)
        self.stream  = self.socket.makefile('w+') # Open file object from file descriptor
        self.debug('Connect')

    def debug(self, message, *args):
        ''' Convenience debugging function '''
        message = message.format(*args)
        self.logger.debug('{} | {}'.format(self.address, message))

    def info(self, message, *args):
        ''' Convenience information function '''
        message = message.format(*args)
        self.logger.info('{} | {}'.format(self.address, message))

    def warn(self, message, *args):
        ''' Convenience warning function '''
        message = message.format(*args)
        self.logger.warn('{} | {}'.format(self.address, message))

    def error(self, message, *args):
        ''' Convenience error function '''
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def exception(self, message, *args):
        ''' Convenience exception function '''
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def handle(self):
        ''' Handle connection '''
        self.debug('Handle')
        raise NotImplementedError

    def finish(self):
        ''' Finish connection by flushing stream, shutting down socket, and
        then closing it '''
        self.debug('Finish')
        try:
            self.stream.flush()
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# HTTP Handler Class

class HTTPHandler(BaseHandler):
    def __init__(self, fd, address, docroot):
        BaseHandler.__init__(self,fd,address,docroot)

    def handle(self):
        ''' Handle connection by reading data and then writing it back until EOF '''
        self.debug('Handle')
        self._parse_request()

        print 'self.uripath'
        self.uripath = os.path.normpath(self.docroot + os.environ['REQUEST_URI'])
        #self.uripath=os.path.normpath(os.environ['REQUEST_URI'])

        print self.uripath
        print 'self.docroot'
        print self.docroot

        if not os.path.exists(self.uripath) or not self.uripath.startswith(self.docroot):
            self._handle_error(404)
        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.X_OK):
            self._handle_script()
        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.R_OK):
            self._handle_file()
        elif os.path.isdir(self.uripath) and os.access(self.uripath,os.R_OK):
            self._handle_directory()
        else:
            self._handle_error(403)


    def _parse_request(self):
        self.debug('Parsing Request')
        os.environ['REMOTE_ADDR'] = self.address.split(':',1)[0]
        
        #Read stream and set REQUEST_METHOD
        data = self.stream.readline().strip().split()

        # parses extra host name, still causing probelms
        try:
            data[1] = data[1].split(os.environ['HTTP_HOST'])[1]
        except:
            pass

        self.debug('Parsing {}'.format(data))
        os.environ['REQUEST_METHOD'] = data[0]
        try:
            os.environ['REQUEST_URI'] = data[1].split('?')[0]
            os.environ['QUERY_STRING'] =data[1].split('?')[1]
        except:
            os.environ['REQUEST_URI'] = data[1]
            os.environ['QUERY_STRING']=''
        data = self.stream.readline().strip().split()
        os.environ['HTTP_HOST'] = data[1]
        
        data = self.stream.readline().strip().split()
        os.environ['HTTP_CONNECTION'] = data[1]

        data = self.stream.readline()
        data = self.stream.readline().strip().split()
        os.environ['HTTP_ACCEPT']=data[1]

        data = self.stream.readline().strip().split()
        os.environ['HTTP_UPGRADE_INSECURE_REQUESTS']=data[1]

        data = self.stream.readline().strip().split(': ')
        os.environ['HTTP_USER_AGENT']=data[1]

        data = self.stream.readline().strip().split(': ')
        os.environ['HTTP_ACCEPT_ENCODING']=data[1]

        data = self.stream.readline().strip().split()
        os.environ['HTTP_ACCEPT_LANGUAGE']=data[1]

        os.environ['HTTP_REFERER']='http://'+os.getenv('HTTP_HOST')+'/'+os.getenv('REQUEST_URI').split('/')[1]

        os.environ['REMOTE_ADDR']=self.address[0]
        os.environ['REMOTE_HOST']=os.getenv('REMOTE_ADDR')
        os.environ['REMOTE_PORT']=self.address[1]

        self.debug('Parsed')

    def _handle_file(self):
        print "in handle file"
        mimetype, _ = mimetypes.guess_type(self.uripath)
        if mimetype is None:
            mimetype = 'application/octet-stream'
        print mimetype
        self.stream.write('HTTP/1.0 200 OK\r\n')
        self.stream.write('Content-Type: {}\r\n'.format(mimetype))
        self.stream.write('\r\n')
        for line in open(self.uripath, 'r+b'):
            #open(self.docroot,'r+b'):
            self.stream.write(line)

    def _handle_directory(self):
        #construct HTML page that lists contents of directory
        print "in handle directory"
        self.stream.write('HTTP/1.0 200 OK\r\n')
        self.stream.write('Content-Type: text/html\r\n')
        self.stream.write('\r\n')
        self.stream.write('''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <title>{}</title>
                <link href="https://www3.nd.edu/~pbui/static/css/blugold.css" rel="stylesheet">
                <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css" rel="stylesheet">
                </head>'''.format(os.path.basename(self.uripath)))
        self.stream.write('''
                <body>
                        <div class="container">
                                <div class="page-header">
                                        <h2>Directory Listing: {}</h2>
                                </div>
                        <table class="table table-striped">
                        <thead>
                        <th>Type</th>
                        <th>Name</th>
                        <th>Size</th>
                        </thead>
                        <tbody>'''.format(os.path.basename(self.uripath)))

        for name in sorted(os.listdir(self.uripath)):
                pathName = os.path.join(self.uripath,name)
                print os.environ['HTTP_HOST'] + pathName.split(self.docroot)[1]
                if os.path.isdir(pathName):
                         self.stream.write('''
                                <tr>
                                        <td><i class="fa fa-folder-o"></i></td>
                                        <td><a href={}>{}</a></td>
                                        <td>-</td>
                                </tr>'''.format(pathName.split(self.uripath)[1], os.path.basename(pathName)))
                if os.path.isfile(pathName):
                        self.stream.write('''
                                <tr>
                                        <td><i class="fa fa-file-o"></i></td>
                                        <td><a href="/{}">{}</a></td>
                                        <td>{}</td>
                                </tr>'''.format(os.environ['HTTP_HOST'] + pathName.split(self.docroot)[1], os.path.basename(pathName), os.path.getsize(pathName)))
        self.stream.write('''
                        </tbody>
                        </table>
                </div>
                </body>
                </html>''')
        #os.environ['REQUEST_URI']
        #os.environ['HTTP_HOST'] +pathName.split(self.docroot)[1],
    
    def _handle_script(self):
        signal.signal(signal.SIGCHLD,signal.SIG_DFL) #set SIGCHLD
        if os.environ['QUERY_STRING'] == '':
            for line in os.popen(self.uripath):
                print line
                self.stream.write(line)
        else:
            print "query string != blank"
            for line in os.popen(self.uripath):
                print line
                self.stream.write(line.format(os.environ['QUERY_STRING'].split('=')[1]))
        signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    def _handle_error(self,error_code):
        print "in error"
        if error_code == '403':
            print error_code
            self.stream.write('HTTP/1.0 {} Forbidden\r\n'.format(error_code))
            self.stream.write('Content-Type: text/html\r\n')
            self.stream.write('\r\n')
            #write image
            self.stream.write('<img src="http://www.icge.co.uk/languagesciencesblog/wp-content/uploads/2014/04/you_shall_not_pass1.jpg">')
        elif error_code == 404:
            print error_code
            self.stream.write('HTTP/1.0 {} Not Found\r\n'.format(error_code))
            self.stream.write('Content-Type: text/html\r\n')
            self.stream.write('\r\n')
            self.stream.write('<img src="http://www.icge.co.uk/languagesciencesblog/wp-content/uploads/2014/04/you_shall_not_pass1.jpg">')

# TCPServer Class

class TCPServer(object):

    def __init__(self, address=ADDRESS, port=PORT, docroot=DOCROOT, handler=HTTPHandler):
        ''' Construct TCPServer object with the specified address, port, and
        handler '''
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = address                                          # Store address to listen on
        self.port    = port                                             # Store port to lisen on
        self.docroot = docroot
        self.handler = handler                                          # Store handler for incoming connections

    def run(self):
        ''' Run TCP Server on specified address and port by calling the
        specified handler on each incoming connection '''
        try:
            # Bind socket to address and port and then listen
            self.socket.bind((self.address, self.port))
            self.socket.listen(BACKLOG)
        except socket.error as e:
            self.logger.error('Could not listen on {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.logger.info('Listening on {}:{}...'.format(self.address, self.port))

        while True:
            # Accept incoming connection
            client, address = self.socket.accept()
            self.logger.debug('Accepted connection from {}:{}'.format(*address))

            # Instantiate handler, handle connection, finish connection
            try:
                handler = self.handler(client, address, self.docroot)
                handler.handle()
            except Exception as e:
                handler.exception('Exception: {}', e)
            finally:
                handler.finish()

# Main Execution

if __name__ == '__main__':
    # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hp:vd:f")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-p':
            PORT = int(value)
        elif option == '-v':
            LOGLEVEL = logging.DEBUG
        elif option == '-d':
            DOCROOT = value
        elif option == '-f':
            FORK = True
        else:
            usage(1)

    # Set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    # Instantiate and run server
    server = TCPServer(ADDRESS,PORT,DOCROOT,HTTPHandler)

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:

