# This file is part of opentsdb-snmp.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
import socket
from random import shuffle
from itertools import cycle
import time
import logging


class Sender(object):
    def __init__(self, tsd_list):
        tsd_list = list(tsd_list)
        shuffle(tsd_list)
        self.tsd_cycle = cycle(tsd_list)
        self.tsd = None

    #init tsd
    def init_tsd(self):
        while (not self.tsd or not self.tsd.verify()):
            (host, port) = next(self.tsd_cycle)
            logging.debug("Using tsd: %s:%d", host, port)
            self.tsd = TSDConnection(host, port)
            self.tsd.connect()
            time.sleep(1)

    def send(self, lines):
        self.init_tsd()
        self.tsd.send_data(lines)


class TSDConnection:
    def __init__(self, host, port):
        self.socket = None
        self.host = host
        self.port = port
        self.last_verify = 0

    def _get_connected_socket(self):
        host = self.host
        port = self.port
        try:
            addresses = socket.getaddrinfo(
                host,
                port,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM, 0)
        except socket.error, msg:
            logging.warning('DNS resolving failed for %s:%d: %s',
                            self.host, self.port, msg)
            return None
        for family, socktype, proto, canonname, sockaddr in addresses:
            try:
                soc = socket.socket(family, socktype, proto)
                soc.settimeout(60)
                soc.connect(sockaddr)
                return soc
            except socket.error, msg:
                logging.warning('Connection attempt failed to %s:%d: %s',
                                self.host, self.port, msg)
                soc.close()
                return None

    def connect(self):
        self.socket = self._get_connected_socket()
        if self.socket:
            return True
        return False

    def verify(self):
        """Periodically verify that our connection to the TSD is OK
        and that the TSD is alive/working."""
        if self.socket is None:
            return False

        # if the last verification was less than a minute ago, don't re-verify
        if self.last_verify and self.last_verify > time.time() - 60:
            return True

        # we use the version command as it is very low effort for the TSD
        # to respond
        # logging.debug('verifying our TSD connection is alive')
        try:
            self.socket.sendall('version\n')
        except socket.error:
            self.socket = None
            return False

        bufsize = 4096
        #dont loop more than 10 times
        for _ in range(10):
            # try to read as much data as we can.  at some point this is going
            # to block, but we have set the timeout low when we made the
            # connection
            try:
                buf = self.socket.recv(bufsize)
            except socket.error:
                self.socket = None
                return False

            # If we don't get a response to the `version' request, the TSD
            # must be dead or overloaded.
            if not buf:
                self.socket = None
                return False

            # Woah, the TSD has a lot of things to tell us...  Let's make
            # sure we read everything it sent us by looping once more.
            if len(buf) == bufsize:
                continue

            break  # TSD is alive.

        # if we get here, we assume the connection is good
        self.last_verify = time.time()
        return True

    def send_data(self, data):
        out = ''
        for line in data:
            logging.debug('SENDING: %s', line)

        out = "\n".join(data)

        if not out:
            logging.debug('send_data no data?')
            return

        # try sending our data.  if an exception occurs, return False
        try:
            self.socket.sendall(out+"\n")
            return True
        except socket.error, msg:
            logging.error('failed to send data: %s', msg)
            try:
                self.socket.close()
            except socket.error:
                pass
            self.socket = None
        return False
