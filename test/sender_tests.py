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
from nose.tools import ok_
import opentsdb.snmp.sender as sender
import time
from mock import patch, Mock
import socket
import signal


class TestDSDConnection(object):
    def setup(self):
        self.tsd = sender.TSDConnection(host='localhost', port=54321)

    def test__get_connected_socket(self):
        #should return None when getaddrinfo raises error

        with patch('socket.getaddrinfo') as mockaddr:
            mockaddr.side_effect = socket.error
            ok_(self.tsd._get_connected_socket() is None)

        with patch('socket.socket') as mocksock:
            mocksock.connect = Mock()
            mocksock.return_value = mocksock
            ok_(self.tsd._get_connected_socket() is not None)
            #raise exception
            mocksock.connect.side_effect = socket.error
            ok_(self.tsd._get_connected_socket() is None)

    def test_connect_verify(self):
        #return false when there's no socket
        ok_(self.tsd.verify() is False)
        #return true when check time is less than 60s
        self.tsd.socket = Mock()
        self.tsd.last_verify = time.time()
        ok_(self.tsd.verify() is True)

        cur_verify_time = time.time() - 60
        self.tsd.last_verify = cur_verify_time

        #pass last_verify, try sockets
        self.tsd.socket.recv = Mock(return_value="test string")
        #should pass
        ok_(self.tsd.verify() is True)
        ok_(self.tsd.last_verify > cur_verify_time)

        self.tsd.last_verify = cur_verify_time
        #should fail and set socket to none because buf is empty
        self.tsd.socket.recv.return_value = None
        ok_(self.tsd.verify() is False)
        ok_(self.tsd.socket is None)

        self.tsd.socket = Mock()
        self.tsd.socket.recv = Mock()

        #fail when error is raised during recv
        self.tsd.socket.recv.side_effect = socket.error
        ok_(self.tsd.verify() is False)

        #connect should return immediately
        with timeout(seconds=1):
            self.tsd.socket = Mock()
            self.tsd.last_verify = time.time()
            self.tsd.connect()

    def test_send_data(self):
        self.tsd.socket = Mock()
        self.tsd.socket.sendall = Mock()
        self.tsd.send_data(["foo", "bar"])
        self.tsd.socket.sendall.assert_called_with('foo\nbar\n')


class TestSender(object):
    def setup(self):
        tsd_list = [('localhost', 4242), ('localhost', 4343)]
        self.sender = sender.Sender(tsd_list)

    def test_sender(self):
        with patch('socket.socket') as mocksock:
            mocksock.connect = Mock()
            mocksock.return_value = mocksock
            mocksock.sendall = Mock()
            self.sender.send(["foo", "bar"])
            mocksock.sendall.assert_called_with('foo\nbar\n')


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise Exception(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)
