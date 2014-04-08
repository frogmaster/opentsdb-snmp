from nose.tools import ok_
import opentsdb.snmp.sender as sender
import time
from mock import patch, Mock
from Queue import Queue
import socket


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

    def test_verify(self):
        #return false when there's no socket
        ok_(self.tsd.verify() is False)
        #return true when check time is less than 60s
        self.tsd.socket = Mock()
        self.tsd.last_verify = time.time()
        ok_(self.tsd.verify() is True)
        #pass last_verify, try sockets
        self.tsd.socket.recv = Mock(return_value="test string")
        cur_verify_time = time.time() - 60
        self.tsd.last_verify = cur_verify_time
        ok_(self.tsd.verify())
        ok_(self.tsd.last_verify > cur_verify_time)

    def test_send_data(self):
        self.tsd.socket = Mock()
        self.tsd.socket.sendall = Mock()
        self.tsd.send_data(["foo", "bar"])
        self.tsd.socket.sendall.assert_called_with('foo\nbar')


class TestSenderThread(object):

    def setup(self):
        self.q = Queue()
        self.st = sender.SenderThread(
            squeue=self.q, host='localhost', port=54321, queue_timeout=0.1)

    def test_mainloopt(self):
        with patch('socket.socket') as mocksock:
            mocksock.connect = Mock()
            mocksock.return_value = mocksock
            self.q.put("foo")
            self.q.put("bar")
            mocksock.sendall = Mock()
            self.st._mainloop()
            mocksock.sendall.assert_called_with('foo\nbar')
            ok_(self.q.empty())
            #test if values are put back to queue, when send_data fails:
            mocksock.sendall.side_effect = socket.error
            self.q.put("foo")
            self.q.put("bar")
            self.st._mainloop()
            ok_(self.q.get() is "foo")
            ok_(self.q.get() is "bar")








#class TestSenderManager(object):
#
#    def setup(self):
#        q = Queue()
#        tsd_list = [("localhost", 54321)]
#        self.sm = SenderManager(squeue=q, tsd_list=tsd_list)
#
#    @patch('opentsdb.snmp.sender.SenderThread')
#    def test_sm_run(self, mocksender):
#        eq_(1, len(self.sm.workers))
#        w = self.sm.workers[0]
#        self.sm.run()
#        self.sm.stop()
