from nose.tools import eq_, ok_
import opentsdb.snmp.main as app
from mock import Mock
from Queue import Queue


class TestConfigReader(object):
    def setup(self):
        self.hlr = app.ConfigReader("misc/sample_data.json")

    def test_load_file(self):
        loaded_data = self.hlr.load_file()
        ok_("devices" in loaded_data)

    def rest_load_devices(self):
        devices = self.hlr.load_devices()
        eq_("foobar", devices[0].hostname)


class TestReaderThread(object):
    def setup(self):
        self.rq = Queue()
        self.sq = Queue()
        self.rthread = app.ReaderThread(rqueue=self.rq, squeue=self.sq)
        self.rthread.start()
        self.mockdevice = Mock()
        self.mockdevice.poll = Mock(return_value=["foo bar"])

    def test_readerthread(self):
        """put stuff in rqueue"""
        self.rq.put(self.mockdevice)
        """wait for queue to join:"""
        self.rq.join()
        data = self.sq.get()
        eq_(data, "foo bar")
        self.rthread.stop()
        self.rthread.join()
