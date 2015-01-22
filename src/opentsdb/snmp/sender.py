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
import multiprocessing
import random
import time
import logging


class SenderManager:
    """
    squeue - queue containing lines for sending to tsds
    tsd_list - list of tuples containing host port pairs
    """
    def __init__(self, squeue, tsd_list):
        self.workers = []
        for host, port in tsd_list:
            for i in range(0, 1):
                st = SenderThread(
                    squeue=squeue,
                    host=host,
                    port=port
                )
                self.workers.append(st)

    def run(self):
        logging.debug("SenderManager: starting senders")
        for w in self.workers:
            w.start()

    def stop(self):
        for w in self.workers:
            w.stop()


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
                soc.settimeout(15)
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
            self.socket.sendall(out)
            return True
        except socket.error, msg:
            logging.error('failed to send data: %s', msg)
            try:
                self.socket.close()
            except socket.error:
                pass
            self.socket = None
        return False


class SenderThread(multiprocessing.Process):
    def __init__(self, squeue, host, port, queue_timeout=5):
        super(SenderThread, self).__init__()
        self.squeue = squeue
        self.host = host
        self.port = port
        self.tsd = TSDConnection(host=host, port=port)
        self._stop = False
        self.daemon = True
        self.queue_timeout = queue_timeout

    def stop(self):
        logging.debug("Stopping SenterThread %s %s", self.host, self.port)
        self._stop = True
        if self.tsd:
            self.tsd.socket = None

    def _mainloop(self):
        senddata = []
        while True:
            try:
                line = self.squeue.get(True, self.queue_timeout)
                senddata.append(line)
                self.squeue.task_done()
                if len(senddata) > 200000:
                    break
            except Exception:
                #logging.debug("Queue empty")
                break
        if len(senddata) > 0:
            self.connect()
            while not self.tsd.send_data(senddata):
                self.connect()
                time.sleep(1)

    def run(self):
        logging.debug("Starting SenterThread %s %s", self.host, self.port)
        while not self._stop:
            self._mainloop()

    def connect(self):
        try_delay = 1
        while not self._stop:
            if self.tsd.verify():
                return True
            try_delay *= 1 + random.random()
            if try_delay > 600:
                try_delay *= 0.5
                time.sleep(try_delay)
            if self.tsd.connect():
                return True
